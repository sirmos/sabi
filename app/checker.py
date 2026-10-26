import base64, json, os, re
from dotenv import load_dotenv

load_dotenv()

SYSTEM = """You are Sabi, a careful pack inspector for Nigerian shoppers. You screen photos of packaged goods (baby food, toothpaste, cosmetics, snacks) for signs of counterfeiting or tampering.
Rules: report only what is visible; use null when unreadable; NEVER say a product is genuine, only report risk signs. A printed NAFDAC number proves nothing until it is looked up, so always copy it exactly. This is a risk screen, not medical advice.
Return ONLY JSON, no markdown, in this shape:
{"brand_as_printed": str|null, "product_name": str|null, "nafdac_number": str|null, "batch_code": str|null,
 "manufacture_date": str|null, "expiry_date": str|null, "date_format": str|null,
 "manufacturer_address_present": bool|null,
 "flags": [{"code": "LOOKALIKE_NAME|DATE_FORMAT_ODD|STICKER_OVER_PRINT|REPRINTED_DATE|NO_NAFDAC_NUMBER|NO_BATCH|NO_MANUFACTURER_ADDRESS|SHELF_LIFE_ODD|POOR_PRINT|OTHER",
           "severity": "low|medium|high", "evidence": str, "where": str}],
 "risk": "low|medium|high|unclear", "summary": str}"""

MOCK = {
    "brand_as_printed": "ORAMAX+", "product_name": "Toothpaste 100g",
    "nafdac_number": "A1-0000", "batch_code": None,
    "manufacture_date": "03-2026", "expiry_date": "03-2028", "date_format": "MM-YYYY with hyphen",
    "manufacturer_address_present": False,
    "flags": [
        {"code": "LOOKALIKE_NAME", "severity": "high", "evidence": "Brand spelling imitates a better-known brand's styling.", "where": "front panel"},
        {"code": "NO_BATCH", "severity": "medium", "evidence": "No batch code is visible.", "where": "crimp or back"},
        {"code": "NO_MANUFACTURER_ADDRESS", "severity": "medium", "evidence": "No manufacturer address is printed.", "where": "back panel"},
    ],
    "risk": "high",
    "summary": "Several risk signs. Verify the NAFDAC number before buying or using this pack.",
}


def _parse(text: str) -> dict:
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start : end + 1])


def check_pack(image: bytes, mime: str) -> dict:
    if os.getenv("SABI_MODE", "mock") == "mock":
        return dict(MOCK, mode="mock")
    from openai import OpenAI

    client = OpenAI(base_url=os.getenv("META_BASE_URL", "https://api.meta.ai/v1"), api_key=os.environ["MODEL_API_KEY"])
    data_url = f"data:{mime};base64,{base64.b64encode(image).decode()}"
    resp = client.chat.completions.create(
        model=os.getenv("SABI_MODEL", "muse-spark-1.3"),
        temperature=0.2,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": [
                {"type": "text", "text": "Inspect this pack and return the JSON."},
                {"type": "image_url", "image_url": {"url": data_url}},
            ]},
        ],
    )
    result = _parse(resp.choices[0].message.content)
    result["mode"] = "live"
    return result
