import json
import re
import urllib.request

UA = {"User-Agent": "Sabi/1.0 (hackathon project; https://github.com/sirmos/sabi)"}
HOSTS = ("world.openfoodfacts.org", "world.openbeautyfacts.org", "world.openproductsfacts.org")


def clean(code: str) -> str:
    return re.sub(r"\D", "", code or "")


def valid(code: str) -> bool:
    """GTIN check digit (EAN-8, UPC-A, EAN-13, GTIN-14)."""
    if len(code) not in (8, 12, 13, 14):
        return False
    d = [int(x) for x in code]
    s = sum(v * (3 if i % 2 == 0 else 1) for i, v in enumerate(reversed(d[:-1])))
    return (10 - s % 10) % 10 == d[-1]


def lookup(code: str) -> dict:
    for host in HOSTS:
        url = f"https://{host}/api/v2/product/{code}.json?fields=product_name,brands,quantity"
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=3) as r:
                j = json.load(r)
            if j.get("status") == 1 and j.get("product"):
                p = j["product"]
                return {"found": True, "source": host.split(".")[1], "name": p.get("product_name"), "brands": p.get("brands")}
        except Exception:
            continue
    return {"found": False}


def check(raw: str) -> dict:
    code = clean(raw)
    out = {"code": code, "valid": valid(code)}
    if out["valid"]:
        out.update(lookup(code))
    else:
        out["found"] = False
    return out
