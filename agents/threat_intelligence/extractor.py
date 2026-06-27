"""Backward-compatible re-exports for IOC extraction."""

from agents.threat_intelligence.ioc_extractor import (
    IOC_TYPE_TO_BREAKDOWN,
    IOCExtractor,
    detect_suspicious_indicators,
    is_private_ipv4,
)

__all__ = [
    "IOCExtractor",
    "IOC_TYPE_TO_BREAKDOWN",
    "detect_suspicious_indicators",
    "is_private_ipv4",
]
