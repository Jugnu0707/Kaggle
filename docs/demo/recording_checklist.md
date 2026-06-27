# Oz AI Demo Video — Recording Checklist

Complete this checklist before recording the official Kaggle demonstration video.

---

## Environment setup

- [ ] Repository cloned and on `main` branch (`git pull`)
- [ ] `python scripts/reset_demo.py` completed successfully
- [ ] Backend running: `http://localhost:8000/api/v1/health` returns 200
- [ ] Frontend running: `http://localhost:5173` loads dashboard
- [ ] Demo incident **Suspicious PowerShell Execution** visible in Incidents list
- [ ] All agent tabs populated (Threat Intel, MITRE, Risk, Response, Executive Report, Guardian, Timeline)
- [ ] Evaluation page (`/evaluation`) shows agent metrics
- [ ] Settings page shows ADK loaded and 5 MCP tools

### For Part 3 (with AI)

- [ ] `GOOGLE_API_KEY` set in `.env` (not visible on screen)
- [ ] `GET /api/v1/ai/test` returns `connected: true` (verify before recording)

### For Part 4 (fallback demo)

- [ ] Second `.env` backup prepared with `GOOGLE_API_KEY` empty OR comment-out ready
- [ ] Re-run `python scripts/reset_demo.py` after key removal tested once
- [ ] Investigation Replay shows `fallback_used: true` on AI-first steps

---

## Browser & display

- [ ] Browser zoom set to **100%** or **110%** (test readability at 1080p)
- [ ] **Dark mode** — Oz AI default theme (do not switch mid-video)
- [ ] Bookmarks bar **hidden**
- [ ] Browser extensions disabled or hidden (password managers, ad blockers)
- [ ] Single browser window — no extra tabs with personal content
- [ ] Resolution: **1920×1080** (1080p) minimum
- [ ] Display scaling: 100% (macOS: default; avoid 125%+ on small screens)
- [ ] Notifications **disabled** (macOS: Do Not Disturb; Windows: Focus Assist)
- [ ] Auto-update / restart prompts disabled during recording window

---

## Terminal (Part 4 only)

- [ ] Terminal font size **14–16pt** minimum
- [ ] Terminal theme matches dark aesthetic (optional)
- [ ] **Full-screen terminal** or large pane — no tiny embedded terminal
- [ ] Working directory: repository root (`Kaggle/`)
- [ ] **No secrets visible** — blur or use `echo` to show empty key, never paste real key
- [ ] Clear terminal history of any accidental key echoes (`clear` before recording)

---

## Cursor & mouse

- [ ] **Cursor hidden when idle** (OBS / QuickTime / ScreenFlow setting) OR steady deliberate movement
- [ ] Mouse pointer size: default or slightly enlarged for visibility
- [ ] Disable cursor highlight trails unless intentional
- [ ] Practice smooth path: Dashboard → Incidents → PowerShell → each tab → Evaluation → Settings

---

## Audio

- [ ] **Microphone tested** — record 30-second test clip and playback
- [ ] Quiet environment — no fan noise, notifications, or background talk
- [ ] Pop filter or distance adjusted to avoid plosives
- [ ] Audio levels: peak around -12 dB to -6 dB (not clipping)
- [ ] Same microphone position for full recording
- [ ] Optional: record narration separately for cleaner edit

---

## Network & stability

- [ ] **Stable network** if using live Gemini (Part 3)
- [ ] Close Dropbox, sync clients, large downloads
- [ ] Backend not under load from parallel test runs
- [ ] Laptop plugged in — not recording on battery saver

---

## Security & privacy

- [ ] **No secrets visible** on screen:
  - [ ] `.env` file — blur or show only `GOOGLE_API_KEY=` with empty value
  - [ ] API docs — do not expand Authorization headers
  - [ ] Browser autofill disabled
  - [ ] GitHub profile — no personal tokens in URL bars
- [ ] Desktop wallpaper professional or neutral
- [ ] No personal email, Slack, or unrelated windows visible

---

## Recording software

- [ ] Software chosen: OBS Studio / QuickTime / ScreenFlow / Loom
- [ ] Frame rate: **30 fps** minimum
- [ ] Capture area: full screen or fixed 1920×1080 region
- [ ] Record **system audio off** if narrating live (avoid double audio)
- [ ] Disk space: ≥2 GB free for raw recording
- [ ] Test 10-second clip — verify text readable when played on phone

---

## Content rehearsal

- [ ] [Demo script](demo_script.md) read once aloud
- [ ] [Storyboard](storyboard.md) tab order practiced
- [ ] Total rehearsal time within **5:00** maximum
- [ ] [FAQ](faq.md) reviewed for potential live questions

---

## Post-recording

- [ ] Raw file backed up before editing
- [ ] Export: **1080p**, H.264 or platform-required format
- [ ] Final duration ≤ **5:00**
- [ ] Upload URL ready for Kaggle submission notebook
- [ ] Optional: captions / subtitles from [narration.md](narration.md)

---

## Quick pre-flight command block

```bash
# From repository root
python scripts/reset_demo.py
curl -s http://localhost:8000/api/v1/health
curl -s http://localhost:5173 | head -1
curl -s http://localhost:8000/api/v1/ai/test | python3 -m json.tool
```

Expected: health 200, frontend HTML, ai test `connected: true` (if key set).

---

## Emergency fallback

If live demo fails during recording:

1. Use pre-seeded data from `reset_demo.py` (tabs already populated)
2. Skip Investigation Runner live run — show Replay from existing run
3. For Part 4, show Replay `fallback_used` flags from offline reset recorded earlier
4. Do not improvise API calls on camera without rehearsal
