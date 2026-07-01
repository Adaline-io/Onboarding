# Adaline Onboarding

Per-client onboarding forms. One folder per client. Each becomes a URL the team sends to the client.

## Live URLs (after GitHub Pages enabled)

- Team index: `https://[username].github.io/adaline-onboarding/`
- BZ Fitness: `https://[username].github.io/adaline-onboarding/bz-fitness/`
- Roca Fuel: `https://[username].github.io/adaline-onboarding/roca-fuel/`

## Structure

```
adaline-onboarding/
├── README.md
├── index.html              ← team-facing directory page
├── bz-fitness/
│   └── index.html          ← client onboarding form
└── roca-fuel/
    └── index.html
```

## Adding a new client

1. Ask Claude to build the onboarding HTML with the new client's data
2. Drop the new folder (e.g. `client-name/index.html`) into this repo
3. Add a link card to the root `index.html`
4. Commit + push — GitHub Pages auto-deploys within ~30 seconds

## Forms data destination

Every submission across all clients lands in the same place:

1. **Google Sheet** — `Adaline Onboarding` Sheet, new row in the `Onboarding` tab (one row per submission, each field its own column)
2. **Google Drive folder** — `Adaline Client Submissions` (PDF + Doc archive of every submission)
3. **Email** — PDF lands in `bettercall@myadaline.com` inbox with subject `[Adaline] Onboarding: [Client]`

All routed through one Apps Script webhook attached to the Sheet. If the webhook ever fails, forms fall back to opening WhatsApp with the structured submission to +91 90481 91616.

## GitHub Pages setup

After uploading files to the repo:
1. Go to **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** → folder: **/ (root)**
4. Save
5. Wait ~30 seconds, refresh — the live URL appears at the top

## Stack

- Single-file static HTML, vanilla JS, no build step, no dependencies
- Inline base64 assets (Adaline wordmark + signs)
- Google Fonts: Space Grotesk + Inter + JetBrains Mono
- Webhook POST to Apps Script with three fallback layers (WhatsApp + clipboard)

— Adaline · The Agency
