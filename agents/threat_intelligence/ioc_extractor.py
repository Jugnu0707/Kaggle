"""Deterministic IOC extraction from evidence text."""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

from agents.threat_intelligence.models import IOC, IOCType

IPV4_PATTERN = re.compile(
    r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d?\d)\b"
)
IPV6_PATTERN = re.compile(
    r"\b(?:[0-9a-fA-F]{1,4}:){2,7}[0-9a-fA-F]{1,4}\b"
    r"|"
    r"\b(?:[0-9a-fA-F]{1,4}:){1,7}:\b"
    r"|"
    r"\b:(?:[0-9a-fA-F]{1,4}:){1,7}[0-9a-fA-F]{1,4}\b"
)
URL_PATTERN = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SHA256_PATTERN = re.compile(r"\b[a-fA-F0-9]{64}\b")
SHA1_PATTERN = re.compile(r"\b[a-fA-F0-9]{40}\b")
MD5_PATTERN = re.compile(r"\b[a-fA-F0-9]{32}\b")
DOMAIN_PATTERN = re.compile(
    r"\b(?!(?:\d{1,3}\.){3}\d{1,3}\b)"
    r"(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,63}\b"
)
HOSTNAME_PATTERN = re.compile(
    r"\b(?:HOST|HOSTNAME|WORKSTATION)=([A-Za-z0-9][A-Za-z0-9._-]{0,62})\b",
    re.IGNORECASE,
)
WINDOWS_USER_PATTERN = re.compile(
    r"\b(?:USER|ACCOUNT)=((?:[A-Za-z0-9._-]+\\)?[A-Za-z0-9._$-]{1,64})\b"
    r"|"
    r"\b([A-Za-z0-9._-]+\\[A-Za-z0-9._$-]{1,64})\b",
    re.IGNORECASE,
)

SUSPICIOUS_KEYWORDS = (
    "powershell",
    "-enc",
    "encodedcommand",
    "failed logon",
    "ransomware",
    "encrypt",
    "mimikatz",
    "lateral",
)

PRIVATE_NETWORKS = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
)

IOC_TYPE_TO_BREAKDOWN = {
    "IPv4": "ipv4",
    "IPv6": "ipv6",
    "Domain": "domain",
    "URL": "url",
    "Email": "email",
    "SHA1": "sha1",
    "SHA256": "sha256",
    "MD5": "md5",
    "Hostname": "hostname",
    "WindowsUsername": "windows_username",
}


def is_private_ipv4(value: str) -> bool:
    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        return False
    return any(address in network for network in PRIVATE_NETWORKS)


def _validate_ipv4(value: str) -> bool:
    try:
        ipaddress.IPv4Address(value)
    except ValueError:
        return False
    return True


def _validate_ipv6(value: str) -> bool:
    try:
        ipaddress.IPv6Address(value)
    except ValueError:
        return False
    return True


def _validate_hash(value: str, length: int) -> bool:
    if len(value) != length or not re.fullmatch(r"[a-fA-F0-9]+", value):
        return False
    return len(set(value.lower())) > 2


def _validate_email(value: str) -> bool:
    if value.count("@") != 1:
        return False
    local, domain = value.split("@", 1)
    return bool(local and domain and "." in domain)


def _validate_domain(value: str) -> bool:
    lowered = value.lower()
    if lowered.endswith(".local") or lowered.endswith(".internal"):
        return True
    labels = lowered.split(".")
    if len(labels) < 2:
        return False
    return all(label and re.fullmatch(r"[a-z0-9-]+", label) for label in labels)


def _validate_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _validate_hostname(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,62}", value))


def _validate_windows_username(value: str) -> bool:
    if "@" in value:
        return False
    if "\\" in value:
        domain, user = value.split("\\", 1)
        return bool(domain and user)
    return bool(re.fullmatch(r"[A-Za-z0-9._$-]{1,64}", value))


def _confidence_for_ioc(ioc_type: IOCType, value: str) -> int:
    if ioc_type in {"SHA256", "SHA1"}:
        return 95
    if ioc_type == "MD5":
        return 90
    if ioc_type == "IPv4":
        return 70 if is_private_ipv4(value) else 90
    if ioc_type == "IPv6":
        return 85
    if ioc_type == "URL":
        lowered = value.lower()
        if any(token in lowered for token in ("powershell", "malware", "payload")):
            return 85
        return 80
    if ioc_type == "Email":
        return 80
    if ioc_type == "Domain":
        return 85
    if ioc_type == "Hostname":
        return 75
    if ioc_type == "WindowsUsername":
        return 70
    return 60


def _infer_source_label(source_hint: str) -> str:
    mapping = {
        "application_log": "Application Log",
        "syslog": "Syslog",
        "web_server_log": "Web Server Log",
        "json": "JSON Log Export",
        "csv": "CSV Log Export",
        "text": "Text Log",
        "evtx": "Windows Event Log",
    }
    lowered = source_hint.lower()
    if "powershell" in lowered:
        return "PowerShell Log"
    return mapping.get(source_hint, "Evidence Log")


def _dedupe_key(ioc_type: IOCType, value: str) -> tuple[str, str]:
    normalized = value.lower()
    if ioc_type in {"SHA1", "SHA256", "MD5"}:
        normalized = value.lower()
    return ioc_type, normalized


class IOCExtractor:
    """Extract and classify IOCs from normalized evidence text."""

    def __init__(self, source_hint: str = "application_log") -> None:
        self.source_label = _infer_source_label(source_hint)

    def extract(self, text: str) -> list[IOC]:
        """Extract validated, deduplicated IOCs from evidence text."""
        if not text.strip():
            return []

        hash_spans = self._collect_hash_spans(text)
        candidates: list[tuple[IOCType, str]] = []

        candidates.extend(
            ("SHA256", match.group(0)) for match in SHA256_PATTERN.finditer(text)
        )
        candidates.extend(
            ("SHA1", match.group(0)) for match in SHA1_PATTERN.finditer(text)
        )
        candidates.extend(
            ("MD5", match.group(0)) for match in MD5_PATTERN.finditer(text)
        )
        candidates.extend(
            ("URL", match.group(0)) for match in URL_PATTERN.finditer(text)
        )
        candidates.extend(
            ("Email", match.group(0)) for match in EMAIL_PATTERN.finditer(text)
        )
        candidates.extend(
            ("IPv4", match.group(0)) for match in IPV4_PATTERN.finditer(text)
        )
        candidates.extend(
            ("IPv6", match.group(0)) for match in IPV6_PATTERN.finditer(text)
        )

        for match in DOMAIN_PATTERN.finditer(text):
            if self._span_overlaps_hash(match.start(), match.end(), hash_spans):
                continue
            candidates.append(("Domain", match.group(0)))

        for match in HOSTNAME_PATTERN.finditer(text):
            candidates.append(("Hostname", match.group(1)))

        for match in WINDOWS_USER_PATTERN.finditer(text):
            value = match.group(1) or match.group(2)
            if value:
                candidates.append(("WindowsUsername", value))

        seen: set[tuple[str, str]] = set()
        iocs: list[IOC] = []

        for ioc_type, raw_value in candidates:
            value = raw_value.strip().rstrip(".,;)")
            if not self._validate(ioc_type, value):
                continue
            key = _dedupe_key(ioc_type, value)
            if key in seen:
                continue
            seen.add(key)
            iocs.append(
                IOC(
                    type=ioc_type,
                    value=value,
                    confidence=_confidence_for_ioc(ioc_type, value),
                    source=self.source_label,
                )
            )

        return sorted(iocs, key=lambda item: (item.type, item.value.lower()))

    def _collect_hash_spans(self, text: str) -> list[tuple[int, int]]:
        spans: list[tuple[int, int]] = []
        for pattern in (SHA256_PATTERN, SHA1_PATTERN, MD5_PATTERN):
            spans.extend(
                (match.start(), match.end()) for match in pattern.finditer(text)
            )
        return spans

    @staticmethod
    def _span_overlaps_hash(
        start: int, end: int, hash_spans: list[tuple[int, int]]
    ) -> bool:
        return any(
            start >= span_start and end <= span_end
            for span_start, span_end in hash_spans
        )

    @staticmethod
    def _validate(ioc_type: IOCType, value: str) -> bool:
        validators = {
            "IPv4": _validate_ipv4,
            "IPv6": _validate_ipv6,
            "SHA256": lambda item: _validate_hash(item, 64),
            "SHA1": lambda item: _validate_hash(item, 40),
            "MD5": lambda item: _validate_hash(item, 32),
            "Email": _validate_email,
            "Domain": _validate_domain,
            "URL": _validate_url,
            "Hostname": _validate_hostname,
            "WindowsUsername": _validate_windows_username,
        }
        validator = validators.get(ioc_type)
        return validator(value) if validator else False


def detect_suspicious_indicators(text: str, iocs: list[IOC]) -> list[str]:
    """Return rule-based suspicious indicator descriptions."""
    findings: list[str] = []
    lowered = text.lower()

    if any(keyword in lowered for keyword in SUSPICIOUS_KEYWORDS):
        if "powershell" in lowered or "-enc" in lowered:
            findings.append(
                "Encoded or suspicious PowerShell activity pattern detected"
            )
        if "failed logon" in lowered or "event=4625" in lowered:
            findings.append("Repeated authentication failure pattern detected")
        if "ransomware" in lowered or "encrypt" in lowered:
            findings.append(
                "File encryption or ransomware-related activity pattern detected"
            )

    external_ips = [
        ioc.value
        for ioc in iocs
        if ioc.type == "IPv4" and not is_private_ipv4(ioc.value)
    ]
    if external_ips:
        findings.append("External IPv4 address observed in evidence entries")

    if any(ioc.type in {"SHA256", "SHA1", "MD5"} for ioc in iocs):
        findings.append("Cryptographic hash values present in evidence")

    if any(ioc.type == "URL" for ioc in iocs):
        findings.append("URL indicators present in evidence")

    return findings
