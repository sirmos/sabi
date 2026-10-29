# Sabi

**Spot the fake before you buy.** Sabi (Pidgin for "to know") helps Nigerian shoppers investigate packaged goods for warning signs of fakes or tampering, and teaches the same skills through a game.

- Live app: https://sabi-rho.vercel.app
- Game: https://sabi-rho.vercel.app/play

## What it does

**Pack checker**
1. Photograph a pack from a few sides.
2. Muse Spark reads the label, copies the NAFDAC number exactly, and returns structured findings: lookalike names, odd date formats, stickers over dates, missing batch codes or manufacturer addresses. When the photos are not enough, it lists the exact extra photos needed.
3. SAM 3.1 outlines the area behind each finding. Tap a finding to see its pin pulse on the photo.
4. Because a printed number proves nothing, Sabi sends the user to NAFDAC's public verify page. The user adds a screenshot of the result and Spark compares the record with the pack: number, product name, product type, manufacturer and expiry.
5. Sabi gives one cautious answer: *Not in NAFDAC's registry*, *Doesn't match the record*, *Record fits, pack has warning signs*, *Looks consistent*, or *Can't tell yet*. It never says a product is genuine.
6. For high or medium results, Sabi drafts a short report the user can copy, email or send on WhatsApp. It contains no personal details.

**Market Run (game)**
Walk four Nigerian markets, inspect stalls that sell different products, and spend earned coins on a lens, a registry check or a trader's tip. Each market has different tricks. Catching a fake unlocks a note based on real NAFDAC alert patterns. A daily case with a twist, streaks and sharing give players a reason to return.

## Meta models used
- **Muse Spark 1.3** (Meta Model API): multi-photo label reading with structured JSON output, and the comparison between the NAFDAC record screenshot and the pack.
- **SAM 3.1** (Meta Model API): locates the area behind each finding. Spark names the concern (for example "sticker" or "date stamp") and SAM returns its box.

## Run it locally
```
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # then add your key
python -m uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000 (checker) and http://127.0.0.1:8000/play (game).

| Setting | Meaning |
|---|---|
| `MODEL_API_KEY` | Meta Model API key |
| `SABI_MODE` | `mock` returns sample results, `live` calls the models |
| `SABI_PROVIDER` | `meta` (default) or `baseten` (experimental) |
| `BASETEN_API_KEY` | Needed only for the `baseten` provider |

`/api/health` shows the mode. `/api/diag` shows the provider, model and a test call without revealing keys.

## Project structure
- `app/main.py`: FastAPI routes (`/api/check`, `/api/match`, pages)
- `app/checker.py`: prompts, model calls, SAM region lookup, mock mode
- `static/index.html`: pack checker page
- `static/play.html`: Market Run game (all art is drawn in code)
- `scripts/`: small API test scripts

## Limits
- Sabi is a risk screen, not proof. Photos can miss details, and a copied registration number on a fake pack can still look valid.
- NAFDAC has no public API that I found, so the user does the lookup on NAFDAC's own page and Sabi reads the screenshot. Nothing is scraped.
- Sabi gives no medical advice. Game packs use fictional brands.

## Privacy
Photos are sent to Meta's model API for analysis and are not stored by Sabi's server. Under Meta's terms for free credits, content may be used for product improvement.
