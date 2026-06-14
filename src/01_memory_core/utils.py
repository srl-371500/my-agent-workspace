# -*- coding: utf-8 -*-
import re, os, json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import quote
try:
    from dotenv import find_dotenv, load_dotenv
except ImportError:
    find_dotenv = load_dotenv = None
ANIM_KW = ["gsap","GSAP","ScrollTrigger","MorphSVG","DrawSVG","MotionPathPlugin","Flip",
    "Observer","Draggable","SplitText","TextPlugin","MotionPath","anime.js","animejs",
    "three.js","THREE","lottie","lottie-web","@motionone","framer-motion",
    "data-animate","data-motion","data-scroll","data-gsap","will-change","@keyframes"]
GATEWAYS = [
    ("https://api.allorigins.win/get?url=", "json"),
    ("https://api.allorigins.win/raw?url=", "raw"),
    ("https://api.codetabs.com/v1/proxy?quest=", "raw+enc"),
    ("https://corsproxy.io/?", "raw+enc"),
]

def read_utf8(p): return Path(p).read_text(encoding="utf-8")
def write_utf8(p, c): Path(p).write_text(c, encoding="utf-8")
def load_env_config(sd=None):
    sd = sd or Path(__file__).resolve().parent; ep = None
    if find_dotenv: ep = find_dotenv(usecwd=True)
    if not ep or not Path(ep).is_file():
        d = sd
        while d != d.parent:
            if (d / ".env").is_file(): ep = str(d / ".env"); break
            d = d.parent
    if ep and load_dotenv: load_dotenv(ep, override=False); print("[ENV] " + ep)
    return {"api_key": os.getenv("LLM_API_KEY",""), "base_url": os.getenv("LLM_BASE_URL","https://api.openai.com/v1").rstrip("/"),
            "model": os.getenv("LLM_MODEL","gpt-4o")}

def call_llm(prompt, cfg, max_tokens=300, temp=0.3):
    ak = cfg.get("api_key","")
    if not ak or ak == "your-api-key-here": return None
    payload = json.dumps({"model":cfg["model"],"messages":[{"role":"user","content":prompt}],
        "temperature":temp,"max_tokens":max_tokens}).encode("utf-8")
    try:
        req = Request(cfg["base_url"]+"/chat/completions", data=payload,
            headers={"Content-Type":"application/json","Authorization":"Bearer "+ak}, method="POST")
        with urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))["choices"][0]["message"]["content"].strip() or None
    except (URLError,HTTPError,KeyError,json.JSONDecodeError) as e: print("[LLM] "+str(e))
    return None

def repair_json(raw):
    try:
        raw = raw.strip()
        f = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", raw, re.DOTALL)
        if f: raw = f.group(1).strip()
        m = re.search(r"[\{\[]", raw)
        if m: raw = raw[m.start():]
        stk, ins, esc = [], False, False
        for ch in raw:
            if esc: esc = False; continue
            if ch == "\\": esc = ins; continue
            if ch == '"' and not esc: ins = not ins; continue
            if ins: continue
            if ch in "{[": stk.append(ch)
            elif ch == "}" and stk and stk[-1] == "{": stk.pop()
            elif ch == "]" and stk and stk[-1] == "[": stk.pop()
        if ins: raw += '"'
        while stk: raw += "}" if stk.pop() == "{" else "]"
        return re.sub(r",\s*([\]}])", r"\1", raw)
    except Exception: return raw

def extract_animations(html_path):
    empty = {"keywords":[],"external_scripts":[],"data_attrs":[],"snippets":[]}
    if not Path(html_path).is_file(): return empty
    content = read_utf8(html_path); r = dict(empty)
    for body in re.findall(r"<script[^>]*>(.*?)</script>", content, re.DOTALL):
        for kw in ANIM_KW:
            if kw in body and kw not in r["keywords"]: r["keywords"].append(kw)
        for m in re.finditer(r"(?:gsap|timeline|ScrollTrigger)[^;{]*[;{][^}]*\}", body, re.DOTALL):
            s = m.group(0).strip()[:200]
            if s not in r["snippets"]: r["snippets"].append(s)
    for src in re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', content):
        if any(kw.lower() in src.lower() for kw in ANIM_KW):
            if src not in r["external_scripts"]: r["external_scripts"].append(src)
            for kw in ANIM_KW:
                if kw.lower() in src.lower() and kw not in r["keywords"]: r["keywords"].append(kw)
    for a in re.findall(r'data-(?:animate|motion|scroll|gsap)[\w-]*', content):
        if a not in r["data_attrs"]: r["data_attrs"].append(a)
    if not r["keywords"]:
        for kw in ANIM_KW:
            if kw in content and kw not in r["keywords"]: r["keywords"].append(kw)
    return r

def summarize_animations(ar):
    p = []
    if ar.get("keywords"): p.append("Lib: "+", ".join(ar["keywords"]))
    if ar.get("external_scripts"): p.append("CDN: "+", ".join(ar["external_scripts"]))
    if ar.get("snippets"): p.append(str(len(ar["snippets"]))+" snippet(s)")
    return " | ".join(p) if p else "None"

def fetch_html(url, timeout=10):
    h = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    print(f"[FETCH] Direct: {url}")
    try:
        req = Request(url, headers=h)
        with urlopen(req, timeout=timeout) as r:
            html = r.read().decode("utf-8", errors="replace")
            if "<html" in html.lower() or "<body" in html.lower():
                print(f"[OK] Direct ({len(html)} bytes)"); return html, "direct"
    except (URLError, HTTPError, OSError) as e: print(f"[WARN] Direct failed: {e}")
    print("[FALLBACK] Engaging cloud gateway self-healing...")
    for gw_tpl, mode in GATEWAYS:
        target = quote(url, safe="") if "enc" in mode else url
        gw_url = gw_tpl + target
        print(f"  -> {gw_tpl[:45]}...")
        try:
            req = Request(gw_url, headers=h)
            with urlopen(req, timeout=25) as r:
                raw = r.read().decode("utf-8", errors="replace")
                html = None
                if mode == "json":
                    data = json.loads(raw)
                    html = data.get("contents", "")
                elif raw and len(raw) > 100:
                    html = raw
                if html and ("<html" in html.lower() or "<body" in html.lower() or len(html) > 500):
                    print(f"[OK] Gateway ({len(html)} bytes)"); return html, gw_tpl[:50]
        except (URLError, HTTPError, OSError) as e: print(f"  [FAIL] {e}")
        except json.JSONDecodeError: print(f"  [FAIL] JSON decode error")
    print("[ERROR] All channels exhausted."); return None, None
