"""Unit tests for secret detection and masking."""

from agents.guardian.secret_detector import detect_secrets, mask_secrets_in_text


def test_detect_secrets_finds_google_api_key() -> None:
    """Google API key patterns are detected."""
    text = "Configured key AIzaSyAbcdefghijklmnopqrstuvwxyz123456"
    findings = detect_secrets(text)
    assert "Google API Key" in findings


def test_mask_secrets_in_text_redacts_values() -> None:
    """Detected secrets are masked in output text."""
    text = "Authorization: Bearer abc.def.ghi"
    masked, findings = mask_secrets_in_text(text)
    assert findings
    assert "[REDACTED_SECRET]" in masked
    assert "Bearer abc.def.ghi" not in masked
