# -*- coding: utf-8 -*-
import re, sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils import read_utf8, write_utf8, load_env_config, call_llm
THRESHOLD = 5
WS = Path(__file__).resolve().parent.parent.parent
SPEC = WS / "docs" / "SPEC.md"

def find_memory():
    for p in [WS / "docs" / "MEMORY.md", WS / "MEMORY.md", Path(__file__).resolve().parent / "MEMORY.md"]:
        if p.exists() and re.search(r"^##\s+.*工作日志", read_utf8(p), re.MULTILINE): return p
    return WS / "docs" / "MEMORY.md"

def parse_log(content):
    entries, in_log, hdr, lines = [], False, None, []
    for line in content.split("\n"):
        if re.match(r"^##\s+.*工作日志", line): in_log = True; continue
        if in_log and line.startswith("## ") and not line.startswith("### "):
            if hdr: entries.append((hdr, "\n".join(lines).strip()))
            break
        if in_log and line.startswith("### "):
            if hdr: entries.append((hdr, "\n".join(lines).strip()))
            hdr, lines = line, []
        elif in_log and hdr is not None: lines.append(line)
    if hdr and in_log: entries.append((hdr, "\n".join(lines).strip()))
    return entries

def summarize(entries, config):
    prompt = ("Compress these work log entries into ONE milestone paragraph (2-4 sentences). "
        "Same language as input.\n\n" + "\n".join(f"{i+1}. {h.strip()}" for i, (h, _) in enumerate(entries)))
    result = call_llm(prompt, config)
    if result: return result
    titles = [re.sub(r"^###\s*\d.*?[-\u2013]\s*", "", h.strip()) for h, _ in entries]
    s = "、".join(titles[:6])
    if len(titles) > 6: s += "等共 " + str(len(titles)) + " 项"
    return s + "。"

def append_milestone(text, dry=False):
    if not SPEC.exists(): return False
    content = read_utf8(SPEC); marker = "## Historical Milestones"
    if marker not in content: content = content.rstrip() + "\n\n" + marker + "\n\n"
    entry = "### " + datetime.now().strftime("%Y-%m-%d") + ": Auto-Archive\n- " + text + "\n"
    if entry in content: return False
    pos = content.find(marker) + len(marker)
    nxt = re.search(r"\n## ", content[pos:])
    ins = pos + nxt.start() if nxt else len(content)
    content = content[:ins].rstrip() + "\n\n" + entry + "\n" + content[ins:]
    if not dry: write_utf8(SPEC, content)
    return True

def clear_log(content):
    out, in_log = [], False
    for line in content.split("\n"):
        if re.match(r"^##\s+.*工作日志", line): out.extend([line, ""]); in_log = True; continue
        if in_log and line.startswith("## ") and not line.startswith("### "): in_log = False
        if not in_log: out.append(line)
    return "\n".join(out)

def main():
    dry = "--dry" in sys.argv; mem = find_memory()
    if not mem.exists(): return 0
    entries = parse_log(read_utf8(mem))
    print(f"[PARSE] {len(entries)} entries (threshold={THRESHOLD})")
    if len(entries) <= THRESHOLD: return 0
    config = load_env_config(); milestone = summarize(entries, config)
    print("[MILESTONE] " + milestone)
    ok = append_milestone(milestone, dry)
    if ok and not dry: write_utf8(mem, clear_log(read_utf8(mem))); print("[MEMORY] Log cleared")
    return 0

if __name__ == "__main__": sys.exit(main())
