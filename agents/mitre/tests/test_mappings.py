"""Unit tests for MITRE mapping rules."""

from agents.mitre.mappings import map_evidence_text
from agents.mitre.service import NO_MAPPING_MESSAGE


def test_powershell_logs_map_to_execution_technique() -> None:
    """PowerShell evidence maps to T1059.001."""
    text = (
        "Suspicious PowerShell Execution\n"
        "2026-06-24T08:15:03Z PROCESS=powershell.exe -EncodedCommand ABC123"
    )
    techniques = map_evidence_text(text)

    assert any(item.technique_id == "T1059.001" for item in techniques)
    powershell = next(item for item in techniques if item.technique_id == "T1059.001")
    assert powershell.technique_name == "PowerShell"
    assert powershell.tactic == "Execution"
    assert "powershell.exe" in powershell.matched_evidence


def test_encoded_powershell_maps_to_obfuscation_technique() -> None:
    """Encoded PowerShell evidence maps to T1027."""
    text = "powershell.exe launched with -EncodedCommand payload"
    techniques = map_evidence_text(text)

    assert any(item.technique_id == "T1027" for item in techniques)
    encoded = next(item for item in techniques if item.technique_id == "T1027")
    assert "-encodedcommand" in encoded.matched_evidence


def test_failed_login_logs_map_to_brute_force() -> None:
    """Failed login evidence maps to T1110."""
    text = "2026-06-24T09:00:00Z EVENT=4625 failed logon for user admin"
    techniques = map_evidence_text(text)

    assert len(techniques) == 1
    assert techniques[0].technique_id == "T1110"
    assert techniques[0].technique_name == "Brute Force"
    assert techniques[0].tactic == "Credential Access"


def test_unknown_logs_return_no_mapping() -> None:
    """Unknown evidence does not match any ATT&CK rule."""
    techniques = map_evidence_text("2026-06-24T10:00:00Z INFO service started normally")
    assert techniques == []
    assert NO_MAPPING_MESSAGE == "No mapping found."
