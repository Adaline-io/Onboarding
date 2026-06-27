# CLAUDE.md — Adaline Onboarding Repo

You're working inside the Adaline Onboarding repository. This file is your operational brief.

## What this repo is

Per-client onboarding forms for **Adaline The Agency** (Myadaline Communications LLP, Calicut). Each subfolder is one client. Each `index.html` is a self-contained single-file HTML form the client fills out at project kickoff.

When the client submits, form data POSTs to a Google Apps Script webhook → lands in the "Adaline Onboarding" Google Sheet as a new row + generates a Google Doc + emails a PDF to bettercall@myadaline.com.

The current owner is **Jareer** (CEO, jareer@). When he opens you in this repo, his goal is usually one of:
1. Push the current state to GitHub
2. Add a new client onboarding
3. Update content in an existing client's form
4. Debug a form submission that didn't reach the Sheet

## File structure

```
adaline-onboarding/
├── CLAUDE.md                       ← this file
├── README.md                       ← human-facing readme
├── index.html                      ← team-facing client directory
├── .gitignore
├── bz-fitness/
│   └── index.html                  ← live onboarding form (149 KB, self-contained)
├── roca-fuel/
│   └── index.html                  ← live onboarding form (149 KB, self-contained)
└── _build/
    ├── README.md                   ← build system overview
    ├── build_bz_onboarding.py      ← regenerates bz-fitness/index.html
    ├── build_roca_onboarding.py    ← regenerates roca-fuel/index.html
    └── assets/                     ← Adaline brand assets (wordmark, signs)
        ├── wordmark_footer.png
        ├── sign_plus.png
        ├── sign_circle.png
        └── sign_cross.png
```

## Tech stack (constraints)

- **Single-file static HTML.** Each onboarding form is one `index.html` with everything inlined — CSS, JS, base64 brand assets. No external dependencies, no build step at serve time. Hosted on GitHub Pages.
- **Vanilla JS.** No React, no framework. Forms use native HTML inputs + a small submit handler that POSTs JSON to the webhook.
- **Build scripts in Python 3.** Run them to regenerate HTMLs after edits. They import `qrcode` for the UPI payment QR (BZ Fitness has a payment block; Roca Fuel does not).
- **Webhook destination is the Google Apps Script** at the URL hardcoded in each build script's `WEBHOOK_URL` constant. If that URL changes, update both scripts and rebuild.

## Brand voice & visual system (do NOT break)

- Dark theme `#0b0b0b` background, `#f5f1ea` ink
- Fonts: Space Grotesk (display) + Inter (body) + JetBrains Mono (utility/code)
- Per-client accent colors (already set, do not change without asking):
  - BZ Fitness: `#ff4d2e` (electric red-orange)
  - Roca Fuel: `#ffd00a` (high-vis yellow)
- Period-style copy in display headlines ("Get in. Let's go.")
- Gaming language for primary CTAs (HIT START → for proposal close; submit button text in onboarding)
- "the Management" voice in all client-facing copy — never use Jareer's name or internal team names in client-facing HTML
- Adaline assets at the close: three signs (+ ○ ×) + wordmark + contact info
- No matched-pair AI sentence structures ("X. Y." then "A. B." back-to-back). Vary rhythm.

## Build system

Each Python script reads brand assets from `./assets/`, embeds them as base64 inside the HTML output, and writes to `../{client}/index.html`. Run from the `_build/` folder:

```bash
cd _build
python3 build_bz_onboarding.py
python3 build_roca_onboarding.py
```

Dependencies (one-time):
```bash
pip install qrcode[pil] --break-system-packages
```

The scripts output ~149 KB self-contained HTML. Don't edit the HTML files directly — always edit the Python build script and regenerate. Editing HTML directly works for quick tweaks but is overwritten the next time the script runs.

## Git workflow — first push to GitHub

When Jareer asks to push to GitHub for the first time:

```bash
cd /path/to/adaline-onboarding

# Initialize and stage
git init
git add .
git commit -m "Initial commit — BZ Fitness + Roca Fuel onboarding forms"

# Create the GitHub repo (requires gh CLI authenticated)
gh repo create adaline-onboarding --public --source=. --description "Per-client onboarding forms for Adaline The Agency" --push

# Enable GitHub Pages (after push)
gh api -X POST "repos/{owner}/adaline-onboarding/pages" \
  -f source[branch]=main \
  -f source[path]=/

# Wait ~30 seconds for first deployment, then check the URL
gh api "repos/{owner}/adaline-onboarding/pages" --jq '.html_url'
```

If `gh` CLI is not installed or not authenticated:
1. Install: `brew install gh` (macOS) or follow https://cli.github.com/
2. Authenticate: `gh auth login` — pick GitHub.com → HTTPS → authenticate with browser
3. Then run the commands above

Fallback (no gh CLI): create the repo via github.com web UI, then `git remote add origin https://github.com/{user}/adaline-onboarding.git && git push -u origin main`.

## Subsequent updates

```bash
git add .
git commit -m "Update {client} — {what changed}"
git push
```

GitHub Pages auto-deploys within ~30 seconds. No build step required on GitHub's side — the HTML is already pre-built.

## Adding a new client

When Jareer asks to add a new client onboarding:

1. **Get the client data** from Jareer if not already provided. You need: client name, project name, project total, deposit amount, accent color (hex), payment schedule split (e.g. 40/40/20), and any project-specific custom fields they need to capture (brand assets, products, hosting, etc.)

2. **Create a new build script** by copying the closest existing one:
   ```bash
   cp _build/build_roca_onboarding.py _build/build_{client_slug}_onboarding.py
   ```
   Edit the new script's `CLIENT` dict, `PAYMENT` dict (if applicable), accent color in CSS, and any client-specific form sections.

3. **Run it:**
   ```bash
   cd _build && python3 build_{client_slug}_onboarding.py
   ```
   This creates `../{client-slug}/index.html` automatically.

4. **Add the client to the team directory** (`index.html` at repo root). Find the `.list` div and add a new `<a class="client" href="./{client-slug}/">` block matching the existing pattern. **Always add it at the top of the list** — the team directory is ordered newest-first, so every new onboarding comes first.

5. **Commit and push:**
   ```bash
   git add . && git commit -m "Add {client} onboarding" && git push
   ```

6. **The live URL** is `https://{github-user}.github.io/adaline-onboarding/{client-slug}/`. Send this to the client.

## Webhook / form submission flow

Every form POSTs to:
```
https://script.google.com/macros/s/AKfycbw03Lw2gCMqJwtt0akBK_roPll_DI90WxX3-2rjH2HRfwunEhfk-nOzTS3LZPknm_2D/exec
```

If a submission doesn't land in the Sheet, the fallback chain is:
1. Webhook POST (no-cors mode — silent on success/failure to the page)
2. Opens WhatsApp at +91 90481 91616 with a structured message containing every form field — client taps Send manually
3. Clipboard backup — entire submission copied as JSON for the client to paste anywhere

Three layers of redundancy. The webhook should work; if Jareer reports forms not arriving, check:
- Apps Script deployment is still "Anyone" access
- Google account didn't revoke permissions
- Try pinging the `/exec` URL in a browser — should return `{"status":"ok","ping":"alive",...}`

## What NOT to do

- Don't change the webhook URL without asking — Jareer's Apps Script is bound to a specific Sheet
- Don't change brand accent colors without asking — they're per-client and signed off
- Don't add tracking pixels, analytics, or third-party scripts — single-file, zero-tracking is part of the trust offer
- Don't reformat copy unless asked — voice is signed off
- Don't break the Adaline asset positioning (signs at close, wordmark in foot block)
- Don't add a backend, framework, or build pipeline — must stay vanilla / pre-built static

## Quick reference

- **Live forms**: `https://{user}.github.io/adaline-onboarding/{client-slug}/`
- **Webhook**: see `WEBHOOK_URL` constant in any `_build/build_*.py`
- **Brand stack**: dark theme, Space Grotesk + Inter + JetBrains Mono, per-client accent
- **Contact**: bettercall@myadaline.com / WhatsApp +91 90481 91616
- **GSTIN**: 32ABYFM6787D1ZN

— Adaline · The Agency
