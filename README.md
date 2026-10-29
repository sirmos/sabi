# Sabi

**Spot the fake before you buy.** Sabi (Pidgin for "to know") helps Nigerian shoppers spot fake or tampered packaged goods, and trains their eye through a game.

- Live demo: https://sabi-rho.vercel.app
- Game: https://sabi-rho.vercel.app/play
- Built for the Meta Global AI Developer Hackathon. Track: Indie Developer. Problem statement: Build for Your World.

## What it does

### 1. Pack checker
1. You photograph a pack from a few sides.
2. Muse Spark reads the label, copies the NAFDAC number exactly, and returns structured findings: lookalike names, odd date formats, stickers over dates, missing batch codes or manufacturer addresses. It lists the exact extra photos it needs when the pictures are not enough.
3. SAM 3.1 outlines each flagged area on the photo with numbered pins.
4. A printed number proves nothing, so Sabi sends the user to NAFDAC's public verify page. The user adds a screenshot of the result and Spark compares the record with the pack (number, product name, product type, manufacturer, expiry).
5. Sabi gives one answer: **Not in NAFDAC's registry**, **Doesn't match the record**, **Record fits, pack has warning signs**, **Looks consistent**, or **Can't tell yet**. It never says a product is genuine.

### 2. Market Run (game)
- Walk four Nigerian markets and inspect stalls selling different products. Each market has different tricks, from lookalike names to shelf-life maths and fake registration numbers.
- Earn coins and spend them on a lens, a registry check, or a trader's tip (traders sometimes fib).
- Catching a fake unlocks a note based on real NAFDAC alert patterns.
- A daily case with a new twist, streaks, stars to unlock markets, and one-tap sharing.

## How it uses Meta models
- **Muse Spark 1.3** (Meta Model API): multi-photo label reading with strict JSON output, and a second call that compares the pack with a screenshot of NAFDAC's registry result, including "Product not found" pages.
- **SAM 3.1** (Meta Model API): Spark names a concern such as "sticker" or "date stamp", and SAM returns the box used for the highlights.
- **Muse Spark Open on Baseten** (optional): set `SABI_PROVIDER=baseten` to run label reading on the open-weight model through Baseten's OpenAI-compatible endpoint.

## Run it locally
```
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # then add your keys
python -m uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000 (checker) and http://127.0.0.1:8000/play (game).

| Setting | Meaning |
|---|---|
| `MODEL_API_KEY` | Meta Model API key |
| `SABI_MODE` | `mock` returns sample results, `live` calls the models |
| `SABI_PROVIDER` | `meta` (default) or `baseten` |
| `BASETEN_API_KEY` | Needed only when the provider is `baseten` |
| `SABI_MODEL`, `META_BASE_URL` | Optional overrides |

`/api/health` shows the mode. `/api/diag` shows the provider, model and a test call without revealing keys.

## Project structure
- `app/main.py`: FastAPI routes (`/api/check`, `/api/match`, pages)
- `app/checker.py`: prompts, model calls, SAM region lookup, mock mode
- `static/index.html`: pack checker page
- `static/play.html`: Market Run game (all art is drawn in code)
- `scripts/`: small test scripts for the Meta and Baseten APIs

## Limits, stated plainly
- Sabi is a risk screen, not proof. A copied registration number on a fake pack can still look valid, and photos cannot prove a product is genuine.
- NAFDAC has no public API that I found, so the lookup is done by the user on NAFDAC's own page and Sabi reads the screenshot. Nothing is scraped.
- Sabi gives no medical advice.
- Game packs use fictional brands.

## Evaluation
Results from testing on real packs will be added here.

## Built during the hackathon
- Oct 26: repository, FastAPI app, Muse Spark label reading, mock mode, mobile UI.
- Oct 26 to 27: SAM 3.1 highlights, multi-photo checks, NAFDAC record comparison, first version of Market Run, Baseten provider switch.
- Oct 27 to 28: four markets with different challenges, product variety, final-verdict logic for unregistered numbers, daily twists, sharing, deployment configuration.
- Oct 29: deployed on Vercel.
