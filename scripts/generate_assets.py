"""Generate architecture diagram and demo screenshots for documentation."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS = REPO_ROOT / "docs"
SCREENSHOTS = DOCS / "screenshots"
WIDTH = 1440
HEIGHT = 900

# Oz AI dark theme palette
BG = (15, 23, 42)
PANEL = (30, 41, 59)
BORDER = (51, 65, 85)
TEXT = (226, 232, 240)
MUTED = (148, 163, 184)
ACCENT = (56, 189, 248)
GREEN = (34, 197, 94)
AMBER = (251, 191, 36)
RED = (248, 113, 113)


def _font(
    size: int, bold: bool = False
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        (
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
            if bold
            else "/System/Library/Fonts/Supplemental/Arial.ttf"
        ),
        "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ),
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _draw_header(draw: ImageDraw.ImageDraw, title: str, subtitle: str) -> None:
    draw.rectangle((0, 0, WIDTH, 64), fill=PANEL)
    draw.text((32, 18), "Oz AI", font=_font(22, True), fill=ACCENT)
    draw.text((120, 22), title, font=_font(18, True), fill=TEXT)
    draw.text((WIDTH - 320, 24), subtitle, font=_font(14), fill=MUTED)


def _draw_sidebar(draw: ImageDraw.ImageDraw, active: str) -> None:
    draw.rectangle((0, 64, 220, HEIGHT), fill=PANEL)
    items = [
        "Dashboard",
        "Incidents",
        "Log Uploads",
        "Evaluation",
        "Reports",
        "Settings",
    ]
    y = 96
    for item in items:
        color = ACCENT if item.lower().startswith(active.lower().split()[0]) else MUTED
        if active == "Incident Details" and item == "Incidents":
            color = ACCENT
        draw.text((28, y), item, font=_font(15), fill=color)
        y += 36


def _panel(
    draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, title: str
) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=12, fill=PANEL, outline=BORDER)
    draw.text((x + 16, y + 14), title, font=_font(14, True), fill=TEXT)


def generate_architecture() -> None:
    img = Image.new("RGB", (1200, 900), BG)
    draw = ImageDraw.Draw(img)
    draw.text((40, 30), "Oz AI — System Architecture", font=_font(28, True), fill=TEXT)

    boxes = [
        (400, 70, 400, 56, "React Dashboard (Frontend)", ACCENT),
        (400, 160, 400, 56, "FastAPI Backend", ACCENT),
        (400, 250, 400, 56, "Coordinator Agent", GREEN),
        (120, 340, 220, 56, "Evidence", GREEN),
        (340, 340, 220, 56, "Threat Intel", GREEN),
        (580, 340, 220, 56, "MITRE", GREEN),
        (820, 340, 220, 56, "Risk", GREEN),
        (120, 420, 220, 56, "Response", GREEN),
        (340, 420, 220, 56, "Executive Report", GREEN),
        (580, 420, 220, 56, "Guardian", AMBER),
        (820, 420, 220, 56, "Timeline", ACCENT),
        (400, 520, 400, 56, "Evaluation Engine", ACCENT),
        (400, 610, 400, 56, "SQLite Database", MUTED),
    ]

    for x, y, w, h, label, color in boxes:
        draw.rounded_rectangle(
            (x, y, x + w, y + h), radius=10, fill=PANEL, outline=color, width=2
        )
        bbox = draw.textbbox((0, 0), label, font=_font(14, True))
        tw = bbox[2] - bbox[0]
        draw.text((x + (w - tw) / 2, y + 18), label, font=_font(14, True), fill=TEXT)

    # Vertical flow arrows
    for y1, y2 in [(126, 160), (216, 250), (306, 340), (476, 520), (576, 610)]:
        draw.line((600, y1, 600, y2), fill=BORDER, width=2)
        draw.polygon([(600, y2), (594, y2 - 8), (606, y2 - 8)], fill=BORDER)

    # Side labels
    draw.rounded_rectangle(
        (40, 250, 240, 370), radius=10, fill=PANEL, outline=ACCENT, width=2
    )
    draw.text((58, 275), "Google ADK", font=_font(14, True), fill=ACCENT)
    draw.text((58, 300), "Runtime + Sessions", font=_font(12), fill=MUTED)
    draw.text((58, 325), "Agent Registry", font=_font(12), fill=MUTED)

    draw.rounded_rectangle(
        (960, 250, 1160, 370), radius=10, fill=PANEL, outline=ACCENT, width=2
    )
    draw.text((978, 275), "MCP Runtime", font=_font(14, True), fill=ACCENT)
    draw.text((978, 300), "5 operational tools", font=_font(12), fill=MUTED)
    draw.text((978, 325), "health · incidents · logs", font=_font(12), fill=MUTED)

    draw.line((240, 310, 400, 280), fill=ACCENT, width=2)
    draw.line((960, 310, 820, 280), fill=ACCENT, width=2)

    draw.text(
        (40, 760),
        "Investigation flow: Coordinator → Agents (with Guardian between stages) → Timeline → Evaluation",
        font=_font(13),
        fill=MUTED,
    )

    output = DOCS / "architecture.png"
    img.save(output)
    print(f"Wrote {output}")


def _severity_color(severity: str) -> tuple[int, int, int]:
    return {
        "Critical": RED,
        "High": AMBER,
        "Medium": ACCENT,
        "Low": GREEN,
    }.get(severity, MUTED)


def screenshot_dashboard() -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    _draw_header(
        draw, "Security Operations Dashboard", "10 incidents · 5 investigations"
    )
    _draw_sidebar(draw, "Dashboard")

    cards = [
        ("Open Incidents", "7", ACCENT),
        ("Critical", "3", RED),
        ("Investigations Running", "4", AMBER),
        ("Logs Uploaded", "25", GREEN),
    ]
    x = 248
    for title, value, color in cards:
        _panel(draw, x, 96, 260, 110, title)
        draw.text((x + 20, 150), value, font=_font(42, True), fill=color)
        x += 280

    _panel(draw, 248, 220, 560, 280, "Recent Incidents")
    rows = [
        ("Suspicious PowerShell Execution", "High", "Investigating"),
        ("Possible Ransomware Activity", "Critical", "Investigating"),
        ("Data Exfiltration to Cloud Storage", "Critical", "Investigating"),
        ("Lateral Movement via SMB", "Critical", "Investigating"),
        ("Credential Dumping via LSASS", "High", "Investigating"),
    ]
    y = 270
    for title, sev, status in rows:
        draw.text((268, y), title, font=_font(14), fill=TEXT)
        draw.text((720, y), sev, font=_font(13), fill=_severity_color(sev))
        draw.text((860, y), status, font=_font(13), fill=MUTED)
        y += 42

    _panel(draw, 820, 220, 380, 280, "Agent Health")
    draw.text((840, 270), "Evidence Agent        98%", font=_font(13), fill=GREEN)
    draw.text((840, 300), "Threat Intelligence     96%", font=_font(13), fill=GREEN)
    draw.text((840, 330), "MITRE Mapping           97%", font=_font(13), fill=GREEN)
    draw.text((840, 360), "Guardian Validator      99%", font=_font(13), fill=GREEN)

    img.save(SCREENSHOTS / "dashboard.png")


def screenshot_incident_detail(
    tab: str, filename: str, content_lines: list[str]
) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    _draw_header(draw, "Suspicious PowerShell Execution", "Incident Details")
    _draw_sidebar(draw, "Incident Details")

    tabs = [
        "Overview",
        "Timeline",
        "Threat Intel",
        "MITRE",
        "Risk",
        "Response",
        "Executive Report",
        "Guardian",
    ]
    x = 248
    for label in tabs:
        color = ACCENT if label.lower().startswith(tab.lower().split()[0]) else MUTED
        if tab == "Threat Intelligence" and label == "Threat Intel":
            color = ACCENT
        if tab == "Executive Report" and label == "Executive Report":
            color = ACCENT
        if tab == "Guardian Audit" and label == "Guardian":
            color = ACCENT
        draw.text((x, 88), label, font=_font(13), fill=color)
        x += 130

    _panel(draw, 248, 120, WIDTH - 272, HEIGHT - 140, tab)
    y = 170
    for line in content_lines:
        draw.text((268, y), line, font=_font(14), fill=TEXT if y < 220 else MUTED)
        y += 32

    img.save(SCREENSHOTS / filename)


def generate_screenshots() -> None:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)

    screenshot_dashboard()
    screenshot_incident_detail(
        "Overview",
        "incident-details.png",
        [
            "Severity: High · Status: Investigating",
            "Source: Microsoft Defender · Confidence: 92%",
            "PowerShell launched by WINWORD.EXE with encoded command.",
            "Evidence: security_events_1042.evtx, powershell_transcript_1042.txt",
            "Uploaded logs: 3 files · Investigation run: completed",
        ],
    )
    screenshot_incident_detail(
        "Evidence",
        "evidence.png",
        [
            "File type: application_log · Total entries: 7",
            "Time range: 2026-06-24T08:15:01Z to 2026-06-24T08:15:40Z",
            "Source: WS-FIN-042 · Detected: PowerShell execution chain",
            "Sample: ProcessCreate WINWORD.EXE → powershell.exe -EncodedCommand",
            "Quality: timestamps present · normalization complete",
        ],
    )
    screenshot_incident_detail(
        "Threat Intelligence",
        "threat-intelligence.png",
        [
            "IOC: 185.234.72.19 · Type: IP · Reputation: Malicious",
            "IOC: stage.ps1 · Type: File · Reputation: Suspicious",
            "Source: offline reputation engine · Confidence: 88%",
            "Matched ransomware C2 patterns from evidence sample.",
        ],
    )
    screenshot_incident_detail(
        "MITRE",
        "mitre.png",
        [
            "T1059.001 — PowerShell · Execution · Confidence 92%",
            "T1105 — Ingress Tool Transfer · Command and Control · 85%",
            "T1055 — Process Injection · Defense Evasion · 78%",
            "Evidence: encoded command, network connect to external IP",
        ],
    )
    screenshot_incident_detail(
        "Risk",
        "risk-assessment.png",
        [
            "Overall Risk: High · Score: 78/100",
            "Likelihood: High · Business Impact: Finance workstation compromise",
            "Priority: P1 · Source: rule-based fallback",
            "Summary: Active execution chain with external C2 indicators.",
        ],
    )
    screenshot_incident_detail(
        "Response",
        "response-plan.png",
        [
            "Containment: Isolate WS-FIN-042 · Block 185.234.72.19",
            "Eradication: Remove staged scripts · Reset credentials for jsmith",
            "Recovery: Restore from backup · Re-enable after validation",
            "Monitoring: Hunt for lateral movement across finance VLAN",
        ],
    )
    screenshot_incident_detail(
        "Executive Report",
        "executive-report.png",
        [
            "Executive Summary: Suspicious PowerShell on finance workstation.",
            "Business Impact: Potential credential theft and data staging.",
            "Recommended actions communicated to IR leadership.",
            "Full markdown report available for export.",
        ],
    )
    screenshot_incident_detail(
        "Guardian Audit",
        "guardian.png",
        [
            "Evidence Agent — PASSED · No injection or PII issues",
            "Threat Intelligence — PASSED · Confidence above threshold",
            "MITRE Mapping — PASSED · Technique IDs validated",
            "Response Plan — PASSED · No unsafe autonomous actions",
        ],
    )
    screenshot_incident_detail(
        "Timeline",
        "timeline.png",
        [
            "08:15:01 — ProcessCreate WINWORD.EXE on WS-FIN-042",
            "08:15:03 — PowerShell spawned with encoded command",
            "08:15:04 — Network connect to 185.234.72.19:443",
            "08:15:40 — Incident escalated to High severity",
        ],
    )

    # Evaluation dashboard
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    _draw_header(draw, "Agent Evaluation Dashboard", "Health score: 94")
    _draw_sidebar(draw, "Evaluation")

    _panel(draw, 248, 96, 280, 120, "Overall Health")
    draw.text((268, 150), "94", font=_font(48, True), fill=GREEN)

    _panel(draw, 488, 96, 280, 120, "Investigation Duration")
    draw.text((508, 150), "4.2s", font=_font(36, True), fill=ACCENT)

    _panel(draw, 768, 96, 280, 120, "MCP Latency")
    draw.text((788, 150), "12ms", font=_font(36, True), fill=ACCENT)

    _panel(draw, 248, 240, WIDTH - 272, HEIGHT - 260, "Agent Benchmarks")
    agents = [
        ("Evidence Agent", "98", "Availability 100 · Reliability 97"),
        ("Threat Intelligence", "96", "Accuracy 94 · Performance 95"),
        ("MITRE Mapping", "97", "Accuracy 96 · Reliability 98"),
        ("Risk Assessment", "95", "Reliability 94 · Performance 93"),
        ("Response Planning", "94", "Availability 96 · Accuracy 92"),
        ("Executive Report", "93", "Reliability 91 · Performance 94"),
        ("Guardian", "99", "Availability 100 · Reliability 99"),
    ]
    y = 290
    for name, score, detail in agents:
        draw.text((268, y), name, font=_font(14), fill=TEXT)
        draw.text((620, y), score, font=_font(14, True), fill=GREEN)
        draw.text((700, y), detail, font=_font(13), fill=MUTED)
        y += 38

    img.save(SCREENSHOTS / "evaluation-dashboard.png")

    # Investigation runner
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    _draw_header(draw, "Investigation Runner", "PowerShell incident · Run in progress")
    _draw_sidebar(draw, "Incidents")

    _panel(draw, 248, 96, WIDTH - 272, HEIGHT - 120, "Pipeline Stages")
    stages = [
        ("Coordinator", True, GREEN),
        ("Evidence", True, GREEN),
        ("Threat Intelligence", True, GREEN),
        ("MITRE Mapping", True, GREEN),
        ("Risk Assessment", True, GREEN),
        ("Response Plan", True, AMBER),
        ("Executive Report", False, MUTED),
        ("Guardian", True, GREEN),
        ("Timeline", False, MUTED),
        ("Evaluation", False, MUTED),
    ]
    y = 140
    for name, done, color in stages:
        marker = "✓" if done else "…"
        draw.text(
            (268, y), f"{marker}  {name}", font=_font(15), fill=color if done else MUTED
        )
        y += 36

    img.save(SCREENSHOTS / "investigation-runner.png")
    print(f"Wrote screenshots to {SCREENSHOTS}")


def main() -> None:
    generate_architecture()
    generate_screenshots()


if __name__ == "__main__":
    main()
