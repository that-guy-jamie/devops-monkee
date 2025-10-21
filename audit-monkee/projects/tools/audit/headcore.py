import json, base64, time
from typing import Dict, Any
try:
    from nacl import signing
    HAVE_NACL = True
except Exception:
    HAVE_NACL = False

def b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip('=')

def build_config(url: str, scores: dict) -> Dict[str, Any]:
    return {
        "site": url,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "version": "1.0.0",
        "seo": {"canonical": True, "robots": "index,follow"},
        "social": {"twitter": {"card": "summary_large_image"}},
        "structured_data": [{"@context":"https://schema.org","@type":"Organization","url":url}],
        "performance": {"preconnect": ["https://fonts.gstatic.com"]},
        "security": {"referrer_policy":"strict-origin-when-cross-origin"},
    }

def sign_config(cfg: Dict[str, Any], private_key_b64url: str) -> Dict[str, Any]:
    if not HAVE_NACL:
        raise RuntimeError("PyNaCl not installed; cannot sign")
    cfg = dict(cfg)
    cfg.pop("signature", None)
    from nacl import signing
    sk = signing.SigningKey(base64.urlsafe_b64decode(private_key_b64url + '==='))
    # Canonical JSON
    def deep_ksort(obj):
        if isinstance(obj, dict):
            return {k: deep_ksort(obj[k]) for k in sorted(obj.keys())}
        if isinstance(obj, list):
            return [deep_ksort(x) for x in obj]
        return obj
    msg = json.dumps(deep_ksort(cfg), separators=(',', ':'), ensure_ascii=False).encode()
    sig = sk.sign(msg).signature
    cfg["signature"] = b64url(sig)
    return cfg
