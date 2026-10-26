"""Checks your key, billing and model. Run: py scripts\\smoke_test.py"""
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url=os.getenv("META_BASE_URL", "https://api.meta.ai/v1"), api_key=os.environ["MODEL_API_KEY"])
r = client.chat.completions.create(
    model=os.getenv("SABI_MODEL", "muse-spark-1.3"),
    messages=[{"role": "user", "content": "In one short Nigerian Pidgin sentence, tell me to check my NAFDAC number."}],
)
print(r.choices[0].message.content)
