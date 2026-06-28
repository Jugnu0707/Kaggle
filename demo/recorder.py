"""Single-file Oz AI demo recorder — produces demo/output/demo.mp4."""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "backend"
BACKEND_PYTHON = BACKEND_ROOT / ".venv" / "bin" / "python"
RESET_SCRIPT = REPO_ROOT / "scripts" / "reset_demo.py"

FRONTEND_URL = "http://localhost:5173"
BACKEND_URL = "http://localhost:8000"
HEALTH_URL = f"{BACKEND_URL}/api/v1/health"
INCIDENTS_URL = f"{BACKEND_URL}/api/v1/incidents"

DEMO_INCIDENT = "Suspicious PowerShell Execution"
MIN_INCIDENTS = 10

OUTPUT_DIR = REPO_ROOT / "demo" / "output"
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"
VIDEO_DIR = OUTPUT_DIR / "video"
FINAL_VIDEO = OUTPUT_DIR / "demo.mp4"
LOG_FILE = OUTPUT_DIR / "log.txt"
SUMMARY_FILE = OUTPUT_DIR / "recording_summary.md"

VIEWPORT = {"width": 1920, "height": 1080}
SLOW_MO_MS = 200
INVESTIGATION_TIMEOUT_MS = 300_000
MAX_VIDEO_SECONDS = 240
TARGET_VIDEO_SECONDS = 180

TABS: tuple[tuple[str, str, str | None], ...] = (
    ("Overview", "overview", None),
    ("Threat Intelligence", "threat_intelligence", "Loading threat intelligence..."),
    ("MITRE ATT&CK", "mitre", "Loading MITRE mappings..."),
    ("Risk Assessment", "risk", "Loading risk assessment..."),
    ("Response Plan", "response", "Loading response plan..."),
    ("Executive Report", "executive_report", "Loading executive report..."),
    ("Guardian Audit", "guardian", "Loading Guardian audit records..."),
    ("Timeline", "timeline", "Loading investigation timeline..."),
)

logger = logging.getLogger("record_demo")
_replay_path: str | None = None
_narration_start = 0.0
_markers: list[str] = []


def _setup_logging() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler(sys.stdout)],
        force=True,
    )


def _mark(label: str) -> None:
    elapsed = int(time.monotonic() - _narration_start)
    minutes, seconds = divmod(elapsed, 60)
    line = f"[{minutes:02d}:{seconds:02d}] {label}"
    print(line, flush=True)
    _markers.append(line)


def _http_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _find_ffmpeg() -> Path:
    system = shutil.which("ffmpeg")
    if system:
        encoders = subprocess.run(
            [system, "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            check=False,
        )
        if "libx264" in encoders.stdout:
            return Path(system)
    try:
        import imageio_ffmpeg

        return Path(imageio_ffmpeg.get_ffmpeg_exe())
    except ImportError:
        pass
    raise RuntimeError(
        "ffmpeg with libx264 is required to produce demo/output/demo.mp4. "
        "Install ffmpeg or run: uv pip install imageio-ffmpeg"
    )


def _ensure_imageio_ffmpeg() -> None:
    try:
        import imageio_ffmpeg  # noqa: F401
    except ImportError:
        if shutil.which("uv"):
            subprocess.check_call(["uv", "pip", "install", "imageio-ffmpeg"], cwd=str(BACKEND_ROOT))
        else:
            subprocess.check_call([str(BACKEND_PYTHON), "-m", "pip", "install", "imageio-ffmpeg"])


def _ensure_playwright() -> None:
    try:
        import playwright  # noqa: F401
    except ImportError:
        if shutil.which("uv"):
            subprocess.check_call(["uv", "pip", "install", "playwright"], cwd=str(BACKEND_ROOT))
        else:
            subprocess.check_call([str(BACKEND_PYTHON), "-m", "pip", "install", "playwright"])
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            browser.close()
    except Exception:
        subprocess.check_call([str(BACKEND_PYTHON), "-m", "playwright", "install", "chromium"])


def _validate_environment(*, reset: bool) -> None:
    _ensure_playwright()
    _ensure_imageio_ffmpeg()
    _find_ffmpeg()

    try:
        health = _http_json(HEALTH_URL)["data"]
    except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as exc:
        raise RuntimeError(f"Backend unavailable at {BACKEND_URL}: {exc}") from exc

    if not health.get("database_connected"):
        raise RuntimeError("Database is not connected.")

    try:
        req = urllib.request.Request(FRONTEND_URL)
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status != 200:
                raise RuntimeError(f"Frontend returned HTTP {resp.status}")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Frontend unavailable at {FRONTEND_URL}: {exc}") from exc

    demo_ok = _demo_data_ok()
    if reset or not demo_ok:
        logger.info("Seeding demo data...")
        subprocess.check_call([str(BACKEND_PYTHON), str(RESET_SCRIPT)], cwd=str(REPO_ROOT))
        if not _demo_data_ok():
            raise RuntimeError("Demo data seeding failed.")


def _demo_data_ok() -> bool:
    try:
        search = _http_json(f"{INCIDENTS_URL}?search=powershell&page_size=20")
        items = search.get("data", {}).get("items", [])
        if not any(i.get("title") == DEMO_INCIDENT for i in items):
            return False
        total = _http_json(f"{INCIDENTS_URL}?page_size=1").get("data", {}).get("total", 0)
        return total >= MIN_INCIDENTS
    except (urllib.error.URLError, TimeoutError, ValueError):
        return False


def _prepare_output() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    VIDEO_DIR.mkdir(parents=True, exist_ok=True)
    for folder in (VIDEO_DIR, SCREENSHOTS_DIR):
        for path in folder.iterdir():
            if path.is_file():
                path.unlink()


def _fail(page: Any, message: str, selector: str | None = None) -> None:
    logger.error("FAIL: %s", message)
    if selector:
        logger.error("Selector: %s", selector)
    if page is not None:
        try:
            page.screenshot(path=str(SCREENSHOTS_DIR / "failure.png"), full_page=True)
        except Exception:
            pass
    raise RuntimeError(message)


def _move_mouse(page: Any, locator: Any) -> None:
    box = locator.bounding_box()
    if not box:
        return
    x = box["x"] + box["width"] / 2
    y = box["y"] + box["height"] / 2
    page.mouse.move(x, y, steps=16)


def _hover(page: Any, locator: Any) -> None:
    locator.wait_for(state="visible", timeout=60_000)
    _move_mouse(page, locator)
    page.wait_for_timeout(400)


def _click(page: Any, locator: Any, *, label: str) -> None:
    try:
        locator.wait_for(state="visible", timeout=60_000)
        _hover(page, locator)
        _move_mouse(page, locator)
        locator.click()
    except Exception as exc:
        _fail(page, f"Click failed: {label}", selector=label)


def _sidebar(page: Any, name: str) -> None:
    link = page.locator("aside nav").get_by_role("link", name=name, exact=True)
    _click(page, link, label=f"sidebar:{name}")


def _wait_loader(page: Any, text: str | None) -> None:
    if not text:
        return
    loader = page.get_by_text(text, exact=True)
    try:
        loader.wait_for(state="visible", timeout=3_000)
    except Exception:
        return
    loader.wait_for(state="hidden", timeout=60_000)


def _shot(page: Any, name: str) -> None:
    path = SCREENSHOTS_DIR / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    logger.info("Screenshot: %s", path)


def _incident_id_from_url(url: str) -> str:
    return url.split("/incidents/")[1].split("/")[0]


def _investigation_status(incident_id: str) -> str | None:
    payload = _http_json(f"{INCIDENTS_URL}/{incident_id}")
    investigation = payload.get("data", {}).get("investigation")
    if not investigation:
        return None
    return investigation.get("investigation_status")


def _latest_replay_path(incident_id: str) -> str | None:
    script = (
        "import uuid\n"
        "from app.db.database import SessionLocal\n"
        "from app.repositories.investigation_run_repository import InvestigationRunRepository\n"
        f"incident_id = uuid.UUID('{incident_id}')\n"
        "session = SessionLocal()\n"
        "runs = InvestigationRunRepository(session).list_by_incident_id(incident_id)\n"
        "session.close()\n"
        "print(runs[-1].id if runs else '')"
    )
    result = subprocess.run(
        [str(BACKEND_PYTHON), "-c", script],
        cwd=str(BACKEND_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    run_id = result.stdout.strip()
    if not run_id:
        return None
    return f"/investigations/{run_id}/replay"


def _wait_for_investigation(page: Any, incident_id: str) -> None:
    deadline = time.monotonic() + (INVESTIGATION_TIMEOUT_MS / 1000)
    while time.monotonic() < deadline:
        try:
            if page.get_by_text("Investigation workflow finished.", exact=True).is_visible():
                return
        except Exception:
            pass
        status = _investigation_status(incident_id)
        if status == "Completed":
            try:
                page.reload(wait_until="domcontentloaded")
                page.get_by_role("heading", name="Investigation Package").wait_for(timeout=30_000)
                return
            except Exception:
                return
        if status == "Failed":
            _fail(page, "Investigation failed", selector="investigation_status=Failed")
        page.wait_for_timeout(2000)
    _fail(page, "Investigation timed out after 5 minutes", selector="Investigation workflow finished.")


def _scene_pause(page: Any, ms: int = 2000) -> None:
    page.wait_for_timeout(ms)


def _scroll_smooth(page: Any) -> None:
    page.evaluate(
        """async () => {
            const step = Math.max(80, Math.floor(window.innerHeight * 0.12));
            const max = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)
              - window.innerHeight;
            if (max <= 0) return;
            let pos = 0;
            while (pos < max) {
              pos = Math.min(max, pos + step);
              window.scrollTo({ top: pos, behavior: 'smooth' });
              await new Promise(r => setTimeout(r, 160));
            }
        }"""
    )
    page.wait_for_load_state("networkidle")


def _run_demo(page: Any) -> None:
    global _replay_path

    page.goto(FRONTEND_URL, wait_until="domcontentloaded")
    page.get_by_text("Oz AI", exact=True).first.wait_for(state="visible")
    page.wait_for_load_state("networkidle")
    _mark("Landing")
    _scene_pause(page, 3000)

    _sidebar(page, "Dashboard")
    page.get_by_role("heading", name="Dashboard").wait_for(state="visible")
    _wait_loader(page, "Loading dashboard...")
    page.get_by_text("Total Incidents").wait_for(state="visible")
    page.get_by_text("Recent Incidents").wait_for(state="visible")
    _mark("Dashboard")
    for label in ("Total Incidents", "Critical Incidents", "Recent Incidents"):
        card = page.get_by_text(label, exact=True).first
        _hover(page, card)
    _shot(page, "dashboard")
    _scene_pause(page)

    _sidebar(page, "Incidents")
    page.get_by_role("heading", name="Incidents").wait_for(state="visible")
    _wait_loader(page, "Loading incidents...")
    _shot(page, "incidents")
    row = page.locator("tbody tr").filter(has_text=DEMO_INCIDENT).first
    _click(page, row, label=f"incident row:{DEMO_INCIDENT}")
    page.get_by_role("heading", name=DEMO_INCIDENT).wait_for(state="visible")
    _wait_loader(page, "Loading incident details...")
    _mark("Incident")
    _scene_pause(page)

    _mark("Problem Statement")
    for term in ("encoded", "PowerShell", "185.234", "WINWORD"):
        target = page.get_by_text(term, exact=False).first
        try:
            _hover(page, target)
        except Exception:
            pass
    _scroll_smooth(page)
    _scene_pause(page)

    _click(page, page.get_by_role("link", name="▶ Start Investigation"), label="Start Investigation link")
    page.get_by_role("heading", name="Investigation Runner").wait_for(state="visible")
    _wait_loader(page, "Loading incident...")
    incident_id = _incident_id_from_url(page.url)
    _mark("Investigation Started")

    status = _investigation_status(incident_id)
    if status == "Completed":
        _mark("Investigation Complete")
        _replay_path = _latest_replay_path(incident_id)
        page.goto(f"{FRONTEND_URL}/incidents/{incident_id}", wait_until="domcontentloaded")
        page.get_by_role("heading", name=DEMO_INCIDENT).wait_for(state="visible")
    else:
        _click(page, page.get_by_role("button", name="▶ Start Investigation"), label="Start Investigation button")
        _wait_for_investigation(page, incident_id)
        page.get_by_role("heading", name="Investigation Package").wait_for(state="visible")
        _replay_path = page.get_by_role("link", name="Replay investigation").get_attribute("href")
        _mark("Investigation Complete")
        _click(page, page.get_by_role("link", name="View incident details"), label="View incident details")
        page.get_by_role("heading", name=DEMO_INCIDENT).wait_for(state="visible")

    for index, (label, screenshot, loader) in enumerate(TABS):
        tab = page.get_by_role("button", name=label, exact=True)
        _click(page, tab, label=f"tab:{label}")
        _wait_loader(page, loader)
        page.get_by_role("heading", name=DEMO_INCIDENT).wait_for(state="visible")
        if label == "Timeline":
            _scroll_smooth(page)
        _mark(label.replace(" ATT&CK", ""))
        _shot(page, screenshot)
        _scene_pause(page, 1800 if index < len(TABS) - 1 else 1500)

    _sidebar(page, "Evaluation")
    page.get_by_role("heading", name="Evaluation Dashboard").wait_for(state="visible")
    _wait_loader(page, "Running evaluation benchmarks...")
    page.get_by_text("Overall Health Score").wait_for(state="visible")
    _mark("Evaluation")
    _shot(page, "evaluation")
    _scene_pause(page)

    if not _replay_path:
        _fail(page, "Replay path missing after investigation", selector="Replay investigation")
    replay_url = _replay_path if _replay_path.startswith("http") else f"{FRONTEND_URL}{_replay_path}"
    page.goto(replay_url, wait_until="domcontentloaded")
    page.get_by_role("heading", name="Investigation Replay").wait_for(state="visible")
    _wait_loader(page, "Loading investigation replay…")
    _mark("Replay")
    _scroll_smooth(page)
    _shot(page, "replay")
    _scene_pause(page)

    _sidebar(page, "Settings")
    page.get_by_role("heading", name="Settings").wait_for(state="visible")
    _wait_loader(page, "Loading system settings...")
    _shot(page, "settings")

    _sidebar(page, "Dashboard")
    page.get_by_role("heading", name="Dashboard").wait_for(state="visible")
    _mark("Dashboard End")


def _convert_webm_to_mp4(source: Path, destination: Path, ffmpeg: Path) -> None:
    if source.suffix.lower() == ".mp4" and source.resolve() != destination.resolve():
        shutil.copyfile(source, destination)
        return
    subprocess.run(
        [
            str(ffmpeg),
            "-y",
            "-i",
            str(source),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(destination),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _probe_video(path: Path, ffmpeg: Path) -> dict[str, Any]:
    result = subprocess.run(
        [str(ffmpeg), "-hide_banner", "-i", str(path), "-f", "null", "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stderr
    width = height = 0
    duration = 0.0
    for line in output.splitlines():
        if "Video:" in line and width == 0:
            parts = line.split(",")
            for part in parts:
                part = part.strip()
                if "x" in part and part[0].isdigit():
                    dims = part.split()[0]
                    if "x" in dims:
                        w, h = dims.split("x", 1)
                        width, height = int(w), int(h)
                        break
        if "Duration:" in line:
            stamp = line.split("Duration:", 1)[1].split(",")[0].strip()
            hours, minutes, seconds = stamp.split(":")
            duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)

    if width == 0 or height == 0 or duration <= 0:
        raise RuntimeError(f"Could not probe video metadata for {path}")

    return {"width": width, "height": height, "duration": duration}


def _trim_video(source: Path, destination: Path, ffmpeg: Path, max_seconds: int) -> None:
    subprocess.run(
        [
            str(ffmpeg),
            "-y",
            "-i",
            str(source),
            "-t",
            str(max_seconds),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(destination),
        ],
        check=True,
        capture_output=True,
        text=True,
    )


def _validate_video(path: Path, ffmpeg: Path) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size < 10_000:
        raise RuntimeError(f"Video missing or too small: {path}")

    info = _probe_video(path, ffmpeg)
    width = int(info["width"])
    height = int(info["height"])
    duration = float(info["duration"])

    if width != VIEWPORT["width"] or height != VIEWPORT["height"]:
        raise RuntimeError(f"Invalid resolution: {width}x{height}, expected 1920x1080")

    if duration <= 0:
        raise RuntimeError("Video duration could not be determined.")

    if duration > MAX_VIDEO_SECONDS + 5:
        raise RuntimeError(f"Video too long: {duration:.1f}s (max {MAX_VIDEO_SECONDS}s)")

    return info


def _write_summary(video_info: dict[str, Any]) -> None:
    shots = sorted(p.name for p in SCREENSHOTS_DIR.glob("*.png"))
    lines = [
        "# Oz AI Demo Recording Summary",
        "",
        f"- **Video:** `{FINAL_VIDEO.relative_to(REPO_ROOT)}`",
        f"- **Duration:** {video_info['duration']:.1f}s",
        f"- **Resolution:** {video_info['width']}x{video_info['height']}",
        f"- **Target length:** ~{TARGET_VIDEO_SECONDS}s (max {MAX_VIDEO_SECONDS}s)",
        "",
        "## Narration markers",
        "",
        *(_markers or ["(none)"]),
        "",
        "## Screenshots",
        "",
        *(f"- `{name}`" for name in shots),
        "",
    ]
    SUMMARY_FILE.write_text("\n".join(lines), encoding="utf-8")


def run_recording() -> int:
    global _narration_start
    _setup_logging()
    _narration_start = time.monotonic()

    try:
        _validate_environment(reset=False)
    except RuntimeError as exc:
        logger.error("%s", exc)
        return 1

    _prepare_output()
    ffmpeg = _find_ffmpeg()

    from playwright.sync_api import sync_playwright

    raw_webm: Path | None = None
    temp_mp4 = VIDEO_DIR / "raw_demo.mp4"

    dark_script = "() => { document.documentElement.classList.add('dark'); }"

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(
                headless=False,
                slow_mo=SLOW_MO_MS,
                args=[
                    "--start-maximized",
                    "--window-size=1920,1080",
                    "--force-device-scale-factor=1",
                    "--disable-dev-shm-usage",
                ],
            )
            context = browser.new_context(
                viewport=VIEWPORT,
                device_scale_factor=1,
                record_video_dir=str(VIDEO_DIR),
                record_video_size=VIEWPORT,
                color_scheme="dark",
            )
            context.add_init_script(dark_script)
            page = context.new_page()
            try:
                _run_demo(page)
            except Exception as exc:
                logger.error("Recording stopped: %s", exc)
                try:
                    page.screenshot(path=str(SCREENSHOTS_DIR / "failure.png"), full_page=True)
                except Exception:
                    pass
                return 1
            finally:
                if page.video:
                    raw_webm = Path(page.video.path())
                context.close()
                browser.close()
    except Exception as exc:
        logger.error("Playwright error: %s", exc)
        return 1

    if raw_webm is None or not raw_webm.exists():
        logger.error("No browser recording was captured.")
        return 1

    try:
        _convert_webm_to_mp4(raw_webm, temp_mp4, ffmpeg)
        info = _validate_video(temp_mp4, ffmpeg)
        if info["duration"] > MAX_VIDEO_SECONDS:
            _trim_video(temp_mp4, FINAL_VIDEO, ffmpeg, MAX_VIDEO_SECONDS)
            info = _validate_video(FINAL_VIDEO, ffmpeg)
        else:
            shutil.move(str(temp_mp4), str(FINAL_VIDEO))
        _validate_video(FINAL_VIDEO, ffmpeg)
        _write_summary(info)
        logger.info("SUCCESS: %s (%.1fs)", FINAL_VIDEO, info["duration"])
        return 0
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        logger.error("Video validation failed: %s", exc)
        return 1
