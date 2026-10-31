import base64, json, os, re
from dotenv import load_dotenv

load_dotenv()

PACK_SYSTEM = """You are Sabi, a careful pack inspector for shoppers in {COUNTRY}. You screen photos of packaged goods (food, baby food, toothpaste, soap, cosmetics, household goods, medicines) for warning signs of counterfeiting or tampering. Photos may show different sides of one pack: combine them.
Rules: report only what is visible; use null when unreadable; NEVER say a product is genuine, only report warning signs. A printed registration, licence or permit number from a national regulator (for example NAFDAC, FDA Ghana, KEBS, FSSAI) proves nothing until it is looked up, so copy it exactly. If key areas are missing or blurry, set risk to "unclear" and list the exact extra photos needed in "retake". Not medical advice. For each flag, "find" is a 1-3 word noun naming one concrete visible object to outline (e.g. "sticker", "barcode", "date stamp", "brand logo") and "image" is the 0-based index of the photo where it is visible. "category" is one of medicine, food, cosmetic (includes toothpaste, soap, lotion, hair and skin products), household, other. "gtin" is the digits printed under the barcode, only if all digits are clearly readable.
Return ONLY JSON:
{"brand_as_printed": str|null, "product_name": str|null, "product_type": str|null, "category": str, "reg_number": str|null, "regulator": str|null, "gtin": str|null, "batch_code": str|null,
 "manufacturer": str|null, "manufacture_date": str|null, "expiry_date": str|null, "date_format": str|null,
 "manufacturer_address_present": bool|null,
 "flags": [{"code": "LOOKALIKE_NAME|DATE_FORMAT_ODD|STICKER_OVER_PRINT|REPRINTED_DATE|NO_REG_NUMBER|NO_BATCH|NO_MANUFACTURER_ADDRESS|SHELF_LIFE_ODD|POOR_PRINT|OTHER",
           "severity": "low|medium|high", "evidence": str, "where": str, "find": str|null, "image": int}],
 "retake": [str], "risk": "low|medium|high|unclear", "summary": str}"""

MATCH_SYSTEM = """You compare a product pack against a record from {REG}, shown in a screenshot (a register entry, a lookup result or an SMS reply). Read the screenshot exactly. Compare what the record shows with the pack: the registration or permit number, product name, product type or category, manufacturer or business name and address, validity status, and whether the pack's expiry date falls after the record's expiry date. A matching number alone is not enough. Never call the pack genuine; say consistent or inconsistent with the record. Some registers identify the business or the quality mark, not the product: then compare only what the record shows and mark the rest cannot_tell. If the screenshot says the product or number was not found, or shows no details, set registry.found=false, leave the other registry fields null, set verdict to "inconsistent", add the check {"item":"Registration number","pack":<the number on the pack>,"registry":null,"result":"mismatch","note":"No record found for this number"} and say in the summary that the number is not in the record (it may also have been misread, so the digits should be re-checked). If the record says the permit or registration is invalid, expired or cancelled, the verdict is "inconsistent". If a record is found and everything it shows fits the pack, the verdict is "consistent" even when the pack's batch or expiry cannot be read: mark those as cannot_tell.
Return ONLY JSON:
{"registry": {"found": bool, "product_name": str|null, "category": str|null, "source": str|null, "manufacturer": str|null, "number": str|null, "approved": str|null, "expiry": str|null},
 "checks": [{"item": str, "pack": str|null, "registry": str|null, "result": "match|mismatch|cannot_tell", "note": str}],
 "verdict": "consistent|inconsistent|unclear", "summary": str}"""

MOCK_PACK = {
    "brand_as_printed": "ORAMAX+", "product_name": "Toothpaste 100g", "product_type": "toothpaste",
    "reg_number": "DEMO-0000", "regulator": "NAFDAC", "category": "cosmetic", "gtin": None, "batch_code": None, "manufacturer": None,
    "manufacture_date": "03-2026", "expiry_date": "03-2028", "date_format": "MM-YYYY with hyphen",
    "manufacturer_address_present": False,
    "flags": [
        {"code": "LOOKALIKE_NAME", "severity": "high", "evidence": "Brand spelling imitates a better-known brand's styling.", "where": "front panel", "find": "brand logo", "image": 0},
        {"code": "NO_BATCH", "severity": "medium", "evidence": "No batch code is visible.", "where": "crimp or back", "find": None, "image": 0},
    ],
    "retake": ["Close-up of the crimp end where the batch code is printed"],
    "regions": [{"image": 0, "label": "lookalike name", "box": {"x1": 15, "y1": 8, "x2": 85, "y2": 30, "w": 100, "h": 100}}],
    "risk": "high", "summary": "Several risk signs. Confirm the registration number before buying or using this pack.",
}
MOCK_MATCH = {
    "registry": {"found": True, "product_name": "SAMPLE CREAM", "category": "Drugs", "source": "Imported Product", "manufacturer": "SAMPLE PHARMA LTD", "number": "DEMO-0000", "approved": "2023-07-27", "expiry": "2028-07-26"},
    "checks": [
        {"item": "NAFDAC number", "pack": "DEMO-0000", "registry": "DEMO-0000", "result": "match", "note": "Numbers are identical."},
        {"item": "Product type", "pack": "toothpaste", "registry": "Drugs", "result": "mismatch", "note": "A toothpaste pack carrying a drug registration is a red flag."},
    ],
    "verdict": "inconsistent", "summary": "The number exists, but it belongs to a different kind of product.",
}


def _parse(text: str) -> dict:
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text[text.find("{") : text.rfind("}") + 1])


def _img(b: bytes, mime: str) -> dict:
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64.b64encode(b).decode()}"}}


def _cfg():
    """Provider for reading labels: Meta Model API (default) or Baseten (Muse Spark Open)."""
    if os.getenv("SABI_PROVIDER", "meta") == "baseten":
        return "https://inference.baseten.co/v1", os.environ["BASETEN_API_KEY"], "meta-models/muse-spark-open-1026"
    return os.getenv("META_BASE_URL", "https://api.meta.ai/v1"), os.environ["MODEL_API_KEY"], os.getenv("SABI_MODEL", "muse-spark-1.3")


def _llm(system: str, parts: list):
    from openai import NotFoundError, OpenAI

    base, key, model = _cfg()
    client = OpenAI(base_url=base, api_key=key)
    cands = [model] + ([m for m in ("muse-spark-1.3", "muse-spark-1.2", "muse-spark-1.1") if m != model] if "api.meta.ai" in base else [])
    tried, last = [], None
    for m in cands:
        try:
            r = client.chat.completions.create(
                model=m, temperature=0.2,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": parts}],
            )
            return _parse(r.choices[0].message.content)
        except NotFoundError as e:
            tried.append(m)
            last = e
    raise RuntimeError("No model found (tried " + ", ".join(tried) + "): " + str(last))


def _live() -> bool:
    return os.getenv("SABI_MODE", "mock") != "mock"


BOX = re.compile(r"<\|box;x1=(\d+);y1=(\d+);x2=(\d+);y2=(\d+);w=(\d+);h=(\d+)")


def locate(image: tuple, phrase: str) -> list:
    """Ask SAM 3.1 to outline `phrase`; return pixel boxes (x2/y2 are inclusive on the wire)."""
    from openai import OpenAI

    client = OpenAI(base_url=os.getenv("META_BASE_URL", "https://api.meta.ai/v1"), api_key=os.environ["MODEL_API_KEY"])
    text = ""
    with client.responses.stream(model="sam-3.1", input=[{"type": "message", "role": "user", "content": [
        {"type": "input_text", "text": phrase}, {"type": "input_image", "image_url": _img(*image)["image_url"]["url"]}]}]) as st:
        for e in st:
            if e.type == "response.output_text.delta":
                text += e.delta
    return [{"x1": int(m[0]), "y1": int(m[1]), "x2": int(m[2]) + 1, "y2": int(m[3]) + 1, "w": int(m[4]), "h": int(m[5])} for m in BOX.findall(text)]


NAMES = {"NG": "Nigeria", "GH": "Ghana", "KE": "Kenya", "IN": "India", "OT": "any country"}
REGS = {"NG": "NAFDAC", "GH": "FDA Ghana", "KE": "KEBS", "IN": "FSSAI", "OT": "the national regulator"}


def check_pack(images: list, country: str = "NG") -> dict:
    if not _live():
        return dict(MOCK_PACK, mode="mock")
    parts = [{"type": "text", "text": "Inspect this pack and return the JSON."}] + [_img(b, m) for b, m in images]
    out = _llm(PACK_SYSTEM.replace("{COUNTRY}", NAMES.get(country, "any country")), parts)
    out["reg_number"] = out.get("reg_number") or out.get("nafdac_number")
    out["nafdac_number"] = out.get("nafdac_number") or out["reg_number"]
    out["regions"] = []
    for f in out.get("flags", [])[:3]:
        if f.get("find"):
            i = min(max(int(f.get("image") or 0), 0), len(images) - 1)
            try:
                boxes = locate(images[i], f["find"])
            except Exception:
                boxes = []
            if boxes:
                out["regions"].append({"image": i, "label": f["code"].replace("_", " ").lower(), "box": boxes[0]})
    return dict(out, mode="live")


def match_registry(pack: dict, image: tuple, country: str = "NG") -> dict:
    if not _live():
        return dict(MOCK_MATCH, mode="mock")
    reg = REGS.get(country, "the national regulator")
    parts = [{"type": "text", "text": "Pack findings:\n" + json.dumps(pack) + "\nThe image is the " + reg + " result. Return the JSON."}, _img(*image)]
    return dict(_llm(MATCH_SYSTEM.replace("{REG}", reg), parts), mode="live")
