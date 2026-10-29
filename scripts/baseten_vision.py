"""Tests whether Muse Spark Open on Baseten can read a pack photo.
Run: python scripts\\baseten_vision.py "C:\\path\\to\\photo.jpg"
Use a photo under about 2 MB (the website shrinks photos before sending them)."""
import base64, mimetypes, os, sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
path = sys.argv[1]
mime = mimetypes.guess_type(path)[0] or "image/jpeg"
url = f"data:{mime};base64,{base64.b64encode(open(path, 'rb').read()).decode()}"
c = OpenAI(base_url="https://inference.baseten.co/v1", api_key=os.environ["BASETEN_API_KEY"])
r = c.chat.completions.create(
    model="meta-models/muse-spark-open-1026",
    messages=[{"role": "user", "content": [
        {"type": "text", "text": "Read this product pack. List the brand, product name, NAFDAC number, batch code and dates exactly as printed. If something cannot be read, say unreadable."},
        {"type": "image_url", "image_url": {"url": url}},
    ]}],
)
print("ANSWER:")
print(r.choices[0].message.content)
