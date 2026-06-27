"""Unit tests for PII detection and masking."""

from agents.guardian.pii_detector import mask_pii_in_text


def test_mask_pii_in_text_masks_email() -> None:
    """Email addresses are masked."""
    masked, blocking, warnings = mask_pii_in_text(
        "Contact analyst@example.com for updates."
    )
    assert "Email Address" in blocking
    assert "[REDACTED_EMAIL]" in masked
    assert "analyst@example.com" not in masked


def test_mask_pii_in_text_warns_on_ip() -> None:
    """IP addresses produce warnings rather than blocking findings."""
    masked, blocking, warnings = mask_pii_in_text("Traffic observed from 192.168.1.10")
    assert "IP Address" in warnings
    assert not blocking
    assert "[REDACTED_IP]" in masked
