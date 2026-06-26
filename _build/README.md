# Build Scripts

Python scripts that regenerate the per-client onboarding HTMLs. Each one reads brand assets from `./assets/`, embeds them as base64, and writes a self-contained `index.html` to the matching client folder one level up.

## Dependencies

```bash
pip install qrcode[pil] --break-system-packages
```

Python 3.10+. No other dependencies — everything else is stdlib.

## Run

```bash
# from inside _build/
python3 build_bz_onboarding.py
python3 build_roca_onboarding.py
```

Output goes to:
- `../bz-fitness/index.html`
- `../roca-fuel/index.html`

Each HTML is ~149 KB. Self-contained — no external CSS, JS, or image refs (except Google Fonts CDN).

## How each script is structured

Top to bottom:

1. **Imports & assets** — loads brand PNGs from `./assets/`, base64-encodes them
2. **Constants** — `WEBHOOK_URL`, `WA_NUMBER`, payment details (BZ Fitness only)
3. **CSS block** — all styles inline
4. **JS block** — submit handler, validation, NPS/star widgets, copy-to-clipboard
5. **Section templates** — hero, company, project, access, payment, submit, success, close
6. **HTML assembly** — single f-string concatenating everything
7. **Output** — writes the final HTML to the client folder

To edit a section's copy, find the template string for that section and modify in place. Re-run the script. Verify the output in the browser.

## Conventions

- `CLIENT` dict or named constants at the top hold per-client data (project name, totals, dates)
- `PAYMENT` dict (BZ Fitness only) holds bank/UPI details used to generate the inline payment block + UPI QR
- Accent colors are CSS variables: `--acc` and `--acc-2`. Set them in the `:root` block of the CSS section.
- Form fields use the pattern `<div class="fld">…</div>` — required fields have `required` attribute; section IDs become section keys in the submitted JSON

## Assets

Bundled in `assets/`:
- `wordmark_footer.png` — Adaline wordmark for the foot block
- `sign_plus.png`, `sign_circle.png`, `sign_cross.png` — three signs above the "Get in. Let's go." close
