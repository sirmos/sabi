import base64, mimetypes, os, sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
path, phrase = sys.argv[1], sys.argv[2]
mime = mimetypes.guess_type(path)[0] or "image/jpeg"
url = f"data:{mime};base64,{base64.b64encode(open(path, 'rb').read()).decode()}"
client = OpenAI(base_url=os.getenv("META_BASE_URL", "https://api.meta.ai/v1"), api_key=os.environ["MODEL_API_KEY"])
with client.responses.stream(
    model="sam-3.1",
    input=[{"type": "message", "role": "user", "content": [
        {"type": "input_text", "text": phrase},
        {"type": "input_image", "image_url": url},
    ]}],
) as s:
    for e in s:
        if e.type == "response.output_text.delta":
            print(e.delta, end="", flush=True)
print()