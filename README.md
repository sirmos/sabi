# Sabi

Sabi (Pidgin: "to know") screens photos of packaged goods for signs of counterfeiting or tampering, then sends the user to NAFDAC to verify the registration number. Built for the Meta Global AI Developer Hackathon.

## Run (Windows PowerShell)
```
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env      # then paste your key into .env
py scripts\smoke_test.py    # needs SABI_MODE irrelevant; tests key + billing
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000. Set `SABI_MODE=live` in `.env` for real Meta Model API calls.

## Built during the hackathon (log)
- 2026-10-26: repo created; scaffold with mock mode, Muse Spark label-reading call, mobile web UI.
