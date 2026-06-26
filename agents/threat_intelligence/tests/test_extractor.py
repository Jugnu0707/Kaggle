"""Threat Intelligence Agent unit tests."""

from agents.threat_intelligence.extractor import IOCExtractor


def test_extract_ipv4_addresses() -> None:
    text = (
        "2026-06-24 HOST=WS-FIN-042 EVENT=NetworkConnect DEST=185.234.72.19:443 "
        "LOCAL=192.168.10.25"
    )
    iocs = IOCExtractor(source_hint="application_log").extract(text)
    values = {ioc.value for ioc in iocs if ioc.type == "IPv4"}
    assert "185.234.72.19" in values
    assert "192.168.10.25" in values


def test_extract_urls() -> None:
    text = "User visited http://malicious.example.com/payload and https://safe.test/a"
    iocs = IOCExtractor().extract(text)
    urls = [ioc.value for ioc in iocs if ioc.type == "URL"]
    assert "http://malicious.example.com/payload" in urls
    assert "https://safe.test/a" in urls


def test_extract_emails() -> None:
    text = "Alert for analyst contact security@example.com and admin@corp.local"
    iocs = IOCExtractor().extract(text)
    emails = [ioc.value for ioc in iocs if ioc.type == "Email"]
    assert "security@example.com" in emails
    assert "admin@corp.local" in emails


def test_extract_hashes() -> None:
    sha256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    sha1 = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
    md5 = "098f6bcd4621d373cade4e832627b4f6"
    text = f"HASH sha256={sha256} sha1={sha1} md5={md5}"
    iocs = IOCExtractor().extract(text)
    types = {ioc.type for ioc in iocs}
    assert "SHA256" in types
    assert "SHA1" in types
    assert "MD5" in types


def test_duplicate_removal() -> None:
    text = "Connect 10.0.0.5 then again 10.0.0.5 and email security@example.com security@example.com"
    iocs = IOCExtractor().extract(text)
    keys = [(ioc.type, ioc.value.lower()) for ioc in iocs]
    assert len(keys) == len(set(keys))


def test_empty_evidence_returns_no_iocs() -> None:
    assert IOCExtractor().extract("") == []
    assert IOCExtractor().extract("   \n  ") == []
