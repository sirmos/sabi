"""Checks your Baseten key. Run: python scripts\\smoke_baseten.py"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
c = OpenAI(base_url="https://inference.baseten.co/v1", api_key=os.environ["BASETEN_API_KEY"])
r = c.chat.completions.create(model="meta-models/muse-spark-open-1026", messages=[{"role": "user", "content": "Reply with one short sentence in Nigerian Pidgin."}])
m = r.choices[0].message
print("CONTENT:", m.content)
print("EXTRA FIELDS:", {k: str(v)[:200] for k, v in (getattr(m, "model_extra", None) or {}).items()})
