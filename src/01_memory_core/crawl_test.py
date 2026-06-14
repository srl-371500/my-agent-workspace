# -*- coding: utf-8 -*-
"""Cloud Gateway Fallback Crawler - 海外站点免代理抓取测试"""
import sys, re
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import fetch_html, extract_animations, summarize_animations, write_utf8

TOOLKIT = Path(__file__).resolve().parent
WS = TOOLKIT.parent.parent
REPORT_DIR = WS / "reports"

def html_to_text(html):
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</(p|div|h[1-6]|li|tr)>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    return "\n".join(l.strip() for l in text.split("\n") if l.strip())

def save_report(url, html, source, anim):
    REPORT_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    domain = re.sub(r"[^a-zA-Z0-9]", "_", re.sub(r"https?://", "", url).split("/")[0])
    fp = REPORT_DIR / f"crawl_{domain}_{ts}.md"
    body = html_to_text(html)[:8000]
    md = f"""# Crawl Report: {url}

| Field | Value |
|-------|-------|
| URL | {url} |
| Time | {datetime.now().isoformat()} |
| Source | {source} |
| HTML Size | {len(html):,} bytes |
| Animations | {summarize_animations(anim)} |

## Extracted Content (head 8000 chars)

{body}
"""
    write_utf8(fp, md)
    return fp

def main():
    url = sys.argv[1] if len(sys.argv) > 1 else "https://news.ycombinator.com/"
    print("=" * 55)
    print(f"Cloud Gateway Fallback Crawler")
    print(f"Target: {url}")
    print("=" * 55)
    html, source = fetch_html(url, timeout=15)
    if not html:
        print("[FATAL] All channels failed."); return 1
    tmp = TOOLKIT / "_tmp_crawl.html"
    write_utf8(tmp, html)
    anim = extract_animations(tmp)
    tmp.unlink(missing_ok=True)
    rp = save_report(url, html, source, anim)
    print(f"\n[DONE] Report: {rp}")
    print(f"[DONE] Animations: {summarize_animations(anim)}")
    print("=" * 55)
    return 0

if __name__ == "__main__":
    sys.exit(main())
