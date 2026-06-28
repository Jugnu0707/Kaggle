# Oz AI — Final Recording Guide

**Purpose:** Technical setup for recording the Kaggle demonstration video.  
**Target duration:** 4 minutes · **Maximum:** 5 minutes

---

## Pre-recording environment

Run from repository root before opening the browser:

```bash
git pull                              # latest main
cp .env.example .env                  # copy if missing
# Set GOOGLE_API_KEY for Part 3 (optional — do not show on screen)
python scripts/reset_demo.py          # 10 incidents, 25 logs, investigations seeded
./scripts/dev.sh                      # or: docker compose up --build
```

### Pre-flight verification

```bash
curl -s -o /dev/null -w "health: %{http_code}\n" http://localhost:8000/api/v1/health
curl -s http://localhost:8000/api/v1/ai/test | python3 -m json.tool
curl -s -o /dev/null -w "frontend: %{http_code}\n" http://localhost:5173/
```

| Check | Expected |
|-------|----------|
| Health | `200` |
| AI test (key set) | `"connected": true` |
| AI test (key empty) | `"connected": false` — OK for Part 4 |
| Frontend | `200` |

Confirm **Suspicious PowerShell Execution** appears on `/incidents` with populated agent tabs.

---

## Screen resolution

| Setting | Value |
|---------|-------|
| **Recording resolution** | 1920×1080 (1080p) minimum |
| **Aspect ratio** | 16:9 |
| **Frame rate** | 30 fps minimum |
| **Display scaling** | 100% (macOS: System Settings → Displays → Default) |
| **Avoid** | 125%+ scaling on small laptops — text becomes illegible at 1080p export |

If using a MacBook with Retina display, set resolution to "Default for display" or an explicit 1920×1080 scaled mode before recording.

---

## Browser setup

| Setting | Value |
|---------|-------|
| **Browser** | Chrome or Firefox (latest) |
| **Zoom** | **100%** — test at 110% only if text is unreadable at 100% |
| **Theme** | **Dark mode** — Oz AI default (`dark:` Tailwind classes); do not switch mid-recording |
| **Window** | Single full-screen window — no split with personal tabs |
| **Bookmarks bar** | Hidden |
| **Extensions** | Disabled or hidden (password managers, ad blockers, grammar tools) |
| **Autofill** | Disabled — prevents credential popups |
| **Starting URL** | http://localhost:5173 |

### Font size

Oz AI uses Tailwind defaults (text-sm / text-base). At 1080p and 100% browser zoom, sidebar labels and tab names must be readable on a phone playback test. If not, increase browser zoom to 110% — not higher.

---

## Terminal setup (Part 4 — AI resilience)

| Setting | Value |
|---------|-------|
| **Font** | Monospace — SF Mono, Menlo, or JetBrains Mono |
| **Font size** | **14–16 pt** minimum |
| **Theme** | Dark background matching dashboard aesthetic |
| **Window size** | Full screen or large pane — not a tiny embedded terminal |
| **Working directory** | Repository root (`Kaggle/`) |
| **History** | Run `clear` before recording — no accidental key echoes |

### Safe commands for on-screen display

```bash
# Show key is empty — never paste a real key
grep GOOGLE_API_KEY .env

# Reset offline demo
python scripts/reset_demo.py
```

Blur the terminal if `.env` content is visible beyond the single variable name.

---

## Notifications and distractions

| Platform | Action |
|----------|--------|
| **macOS** | Enable Do Not Disturb / Focus — allow only screen recording app |
| **Windows** | Enable Focus Assist — alarms only |
| **Both** | Quit Slack, email, Messages, Dropbox sync, OS update prompts |
| **Phone** | Silent mode — out of frame |
| **Calendar** | No meeting reminders during recording window |

---

## Cursor and mouse

| Setting | Recommendation |
|---------|----------------|
| **Cursor hidden when idle** | Enable in OBS Studio (Settings → General → ☑ Move source using cursor) or use a tool that hides cursor after 2s idle |
| **Alternative** | Keep cursor moving deliberately — never leave static over sensitive areas |
| **Pointer size** | macOS: System Settings → Accessibility → Display → Pointer → slightly enlarged |
| **Trails / highlights** | Optional — use consistently or not at all |
| **Practiced path** | Dashboard → Incidents → PowerShell → Investigate → each tab → Evaluation → Replay/Terminal |

Rehearse tab clicks twice — UI tabs are: Overview, Timeline, Threat Intelligence, MITRE ATT&CK, Risk Assessment, Response Plan, Executive Report, Guardian Audit.

---

## Microphone checklist

- [ ] Microphone selected in recording software (not built-in laptop mic if avoidable)
- [ ] 30-second test recording played back — no clipping, no room echo
- [ ] Quiet environment — HVAC, fans, street noise minimized
- [ ] Consistent distance from mic (15–20 cm with pop filter, or 30 cm without)
- [ ] Peak levels between **-12 dB and -6 dB** — not clipping at 0 dB
- [ ] Same mic position for entire session
- [ ] Optional: record narration separately in Audacity and sync in post — cleaner than live if room is noisy
- [ ] System audio **muted** in recording if narrating live (avoid double audio from notification sounds)

---

## Recording software

| Option | Notes |
|--------|-------|
| **OBS Studio** | Free — 1080p, cursor hide, separate audio tracks |
| **QuickTime** | macOS built-in — simple full-screen capture |
| **ScreenFlow / Camtasia** | Paid — easier editing |
| **Loom** | Quick upload — verify 1080p export available |

Settings:

- Capture: full display or fixed 1920×1080 region
- Format: MP4 H.264 (widely accepted)
- Disk space: ≥ 2 GB free for raw file
- Record a **10-second test clip** and play on phone — verify text readability

---

## Security — nothing sensitive on screen

- [ ] `.env` never opened with real `GOOGLE_API_KEY` value visible
- [ ] Swagger `/docs` — do not expand Authorization headers
- [ ] No personal bookmarks, email tabs, or tokens in URL bar
- [ ] GitHub login bar shows no personal access tokens
- [ ] Desktop wallpaper neutral or solid color
- [ ] Terminal history cleared of any API key paste attempts

---

## Two-pass recording strategy (recommended)

| Pass | Setup | Covers |
|------|-------|--------|
| **Pass A** | `GOOGLE_API_KEY` set (optional) | Parts 1–3 and 5 — live demo with populated tabs |
| **Pass B** | `GOOGLE_API_KEY` empty, `reset_demo.py` | Part 4 — fallback and replay badges |

Edit passes together in post. Safer than toggling API key mid-recording.

---

## Post-recording

- [ ] Raw file backed up before editing
- [ ] Final export: 1080p H.264, ≤ 5:00 duration
- [ ] Audio normalized — no sudden volume jumps between passes
- [ ] Upload to YouTube (unlisted) or Vimeo for Kaggle submission URL
- [ ] Optional captions from [FINAL_DEMO_SCRIPT.md](FINAL_DEMO_SCRIPT.md)

---

## Emergency fallback during recording

If live demo fails on camera:

1. Use pre-seeded data from `reset_demo.py` — tabs already populated
2. Skip live Investigation Runner — show completed pipeline from seeded run
3. For Part 4, cut to pre-recorded replay clip showing `fallback_used: true`
4. Use static screenshots from `docs/screenshots/` as B-roll
5. Do not improvise untested API calls on camera

---

## Related documents

- [FINAL_DEMO_SCRIPT.md](FINAL_DEMO_SCRIPT.md)
- [FINAL_STORYBOARD.md](FINAL_STORYBOARD.md)
- [CHECKLIST.md](CHECKLIST.md)
