# Sabi

**Spot the fake before you buy.** Sabi (Pidgin for "to know") helps shoppers investigate packaged goods for warning signs of fakes or tampering, then confirm what they can against the official register in their country. It also teaches the same skills through a game.

- Live app: https://sabi-rho.vercel.app
- Game: https://sabi-rho.vercel.app/play

## What it does

**Pack checker**
1. Choose your country and photograph a pack from a few sides.
2. Muse Spark reads the label, copies the registration number exactly, and returns structured findings: lookalike names, odd date formats, stickers over dates, missing batch codes or manufacturer addresses. When the photos are not enough, it lists the exact extra photos needed.
3. SAM 3.1 outlines the area behind each finding. Tap a finding to see its pin pulse on the photo.
4. **Barcode check:** if the barcode digits are readable, Sabi checks the check digit and looks the code up in the open Open Food Facts, Open Beauty Facts and Open Products Facts databases. These are crowd-sourced, so a miss is common for local products and a mismatch is a prompt to double-check, not proof.
5. **Official register:** a printed number proves nothing until it is looked up. Sabi sends the user to the official source for their country. The user adds a screenshot of the result and Spark compares the record with the pack. Nothing is scraped.
6. Sabi gives one cautious answer. It never says a product is genuine. When no official public register applies to that kind of product in the chosen country, Sabi says so and judges the pack on the pack and barcode evidence alone.
7. For high or medium results, Sabi drafts a short report the user can copy, email or send on WhatsApp. It contains no personal details.

**Country packs**
| Country | Official source Sabi links to | Notes |
|---|---|---|
| Nigeria | NAFDAC (NAPAMS verify page) | Medicines, food, cosmetics and other regulated goods |
| Ghana | FDA Ghana public product registry | Medicines, food, cosmetics |
| Kenya | KEBS Standardization Mark verification by SMS to 20023 | Mark permits, not individual products |
| India | FSSAI FoSCoS FBO search | Identifies the food business, not the product |
| Another country | None yet | Pack and barcode evidence only, stated plainly |

Many countries have no public per-product register for food or cosmetics, so Sabi does not claim to verify those against an official source.

**Market Run (game)**
Walk four Nigerian markets, inspect stalls that sell different products, and spend earned coins on a lens, a registry check or a trader's tip. Each market has different tricks. Catching a fake unlocks a note based on real NAFDAC alert patterns. A daily case with a twist, streaks and sharing give players a reason to return.

## Meta models used
- **Muse Spark 1.3** (Meta Model API): multi-photo label reading with structured JSON output, and the comparison between a register screenshot and the pack.
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
- `app/main.py`: FastAPI routes (`/api/check`, `/api/match`, `/api/barcode`, pages)
- `app/checker.py`: prompts, model calls, SAM region lookup, mock mode
- `app/barcode.py`: barcode check digit and open-database lookup
- `static/index.html`: pack checker page and country packs
- `static/play.html`: Market Run game (all art is drawn in code)
- `scripts/`: small API test scripts

## Limits
- Sabi is a risk screen, not proof. Photos can miss details, and a copied registration number on a fake pack can still look valid.
- Registers differ by country and product type. Kenya's check covers quality-mark permits and India's covers food businesses, not individual products.
- Barcode prefixes show where a company licensed its prefix, not where a product was made or sold, so Sabi does not treat a foreign prefix as a warning sign.
- Sabi gives no medical advice. Game packs use fictional brands.

## Privacy
Photos are sent to Meta's model API for analysis and are not stored by Sabi's server. Under Meta's terms for free credits, content may be used for product improvement.
