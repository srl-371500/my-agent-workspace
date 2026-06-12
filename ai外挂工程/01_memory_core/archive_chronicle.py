"""
Archive Chronicle Script - AI-Powered Memory Compression
Reads MEMORY.md work log entries, summarizes them via mimo API,
appends milestones to SPEC.md, and prunes the log.

Usage:
  python archive_chronicle.py          # normal run
  python archive_chronicle.py --dry    # dry run (no writes)
"""

import re
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

try:
    from dotenv import find_dotenv, load_dotenv
except ImportError:
    find_dotenv = None
    load_dotenv = None

SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
MEMORY_PATH_ROOT = WORKSPACE_ROOT / "MEMORY.md"
MEMORY_PATH_LOCAL = SCRIPT_DIR / "MEMORY.md"
SPEC_PATH = SCRIPT_DIR / "SPEC.md"

CHRONICLE_THRESHOLD = 5


def resolve_memory_path():
    if MEMORY_PATH_ROOT.exists():
        content = MEMORY_PATH_ROOT.read_text(encoding="utf-8")
        if re.search(r"^##\s+.*工作日志", content, re.MULTILINE):
            return MEMORY_PATH_ROOT

    if MEMORY_PATH_LOCAL.exists():
        content = MEMORY_PATH_LOCAL.read_text(encoding="utf-8")
        if re.search(r"^##\s+.*工作日志", content, re.MULTILINE):
            return MEMORY_PATH_LOCAL

    return MEMORY_PATH_ROOT


def load_env_config():
    env_path = None

    if find_dotenv:
        env_path = find_dotenv(usecwd=True)

    if not env_path or not Path(env_path).is_file():
        candidate = SCRIPT_DIR.parent / ".env"
        if candidate.is_file():
            env_path = str(candidate)
        else:
            example = SCRIPT_DIR.parent / ".env.example"
            if example.is_file():
                env_path = str(example)

    if env_path and load_dotenv:
        load_dotenv(env_path, override=False)
        print("[ENV] Loaded: " + env_path)
    else:
        print("[ENV] No .env file found, using environment variables only")

    api_key = os.getenv("LLM_API_KEY", "")
    base_url = os.getenv("LLM_BASE_URL", "https://token-plan-sgp.xiaomimimo.com/v1")
    model = os.getenv("LLM_MODEL", "mimo-v2.5")

    return {
        "api_key": api_key,
        "base_url": base_url.rstrip("/"),
        "model": model,
    }


def parse_work_log_entries(content):
    entries = []
    in_log = False
    current_entry = None
    current_lines = []

    for line in content.split("\n"):
        if re.match(r"^##\s+.*工作日志", line):
            in_log = True
            continue

        if in_log and line.startswith("## ") and not line.startswith("### "):
            if current_entry:
                entries.append((current_entry, "\n".join(current_lines).strip()))
            break

        if in_log and line.startswith("### "):
            if current_entry:
                entries.append((current_entry, "\n".join(current_lines).strip()))
            current_entry = line
            current_lines = []
        elif in_log and current_entry is not None:
            current_lines.append(line)

    if current_entry and in_log:
        entries.append((current_entry, "\n".join(current_lines).strip()))

    return entries


def call_mimo_summarize(entries, config):
    if not config["api_key"] or config["api_key"] == "your-api-key-here":
        print("[MIMO] No valid API key, using local fallback summary")
        return generate_local_summary(entries)

    entries_text = ""
    for i, (header, body) in enumerate(entries, 1):
        first_line = body.split("\n")[0] if body else ""
        entries_text += str(i) + ". " + header.strip() + "\n   " + first_line.strip() + "\n\n"

    prompt = (
        "You are a project milestone summarizer. "
        "Compress the following work log entries into ONE concise milestone paragraph "
        "(2-4 sentences). Focus on what was achieved, not implementation details. "
        "Write in the same language as the input entries.\n\n"
        "Work Log Entries:\n" + entries_text
    )

    url = config["base_url"] + "/chat/completions"
    payload = json.dumps({
        "model": config["model"],
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 300,
    }).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + config["api_key"],
    }

    try:
        req = Request(url, data=payload, headers=headers, method="POST")
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            summary = data["choices"][0]["message"]["content"].strip()
            if summary:
                print("[MIMO] Summary generated (" + str(len(summary)) + " chars)")
                return summary
            else:
                print("[MIMO] Empty response, using local fallback")
                return generate_local_summary(entries)
    except (URLError, HTTPError, KeyError, json.JSONDecodeError) as e:
        print("[MIMO] API call failed: " + str(e))
        print("[MIMO] Falling back to local summary")
        return generate_local_summary(entries)


def generate_local_summary(entries):
    titles = []
    for header, _ in entries:
        title = re.sub(r"^###\s*\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}\s*[-\u2013]\s*", "", header.strip())
        titles.append(title)

    summary = "、".join(titles[:6])
    if len(titles) > 6:
        summary += "等共 " + str(len(titles)) + " 项任务"
    summary += "。"
    return summary


def append_milestone_to_spec(milestone_text, dry_run=False):
    if not SPEC_PATH.exists():
        print("[WARN] SPEC.md not found at " + str(SPEC_PATH))
        return False

    content = SPEC_PATH.read_text(encoding="utf-8")

    milestone_marker = "## Historical Milestones"
    if milestone_marker not in content:
        content = content.rstrip() + "\n\n" + milestone_marker + "\n\n"

    today = datetime.now().strftime("%Y-%m-%d")
    new_milestone = "### " + today + ": Chronicle Auto-Archive\n- " + milestone_text + "\n"

    if new_milestone in content:
        print("[SPEC] Milestone already exists for today, skipping")
        return False

    marker_pos = content.find(milestone_marker)
    section_start = marker_pos + len(milestone_marker)

    next_section = re.search(r"\n## ", content[section_start:])
    if next_section:
        insert_pos = section_start + next_section.start()
    else:
        insert_pos = len(content)

    before = content[:insert_pos].rstrip()
    after = content[insert_pos:]
    content = before + "\n\n" + new_milestone + "\n" + after

    if dry_run:
        print("[DRY-RUN] Would append milestone to SPEC.md")
        return True

    SPEC_PATH.write_text(content, encoding="utf-8")
    print("[SPEC] Milestone appended to " + SPEC_PATH.name)
    return True


def clear_work_log(content):
    lines = content.split("\n")
    new_lines = []
    in_log = False

    for line in lines:
        if re.match(r"^##\s+.*工作日志", line):
            new_lines.append(line)
            new_lines.append("")
            in_log = True
            continue

        if in_log and line.startswith("## ") and not line.startswith("### "):
            in_log = False
            new_lines.append(line)
            continue

        if in_log:
            continue

        new_lines.append(line)

    return "\n".join(new_lines)


def main():
    dry_run = "--dry" in sys.argv

    print("=" * 55)
    print("Archive Chronicle Script - AI Memory Compression")
    print("=" * 55)
    if dry_run:
        print("[MODE] DRY RUN - no files will be modified")

    memory_path = resolve_memory_path()
    print("  Workspace root: " + str(WORKSPACE_ROOT))
    print("  MEMORY.md:      " + str(memory_path))
    print("  SPEC.md:        " + str(SPEC_PATH))
    print()

    if not memory_path.exists():
        print("[INFO] MEMORY.md not found. Nothing to process.")
        return 0

    config = load_env_config()
    print()

    content = memory_path.read_text(encoding="utf-8")
    entries = parse_work_log_entries(content)

    print("[PARSE] Found " + str(len(entries)) + " work log entries in MEMORY.md")
    print("[THRESHOLD] Archive triggers at > " + str(CHRONICLE_THRESHOLD) + " entries")

    if len(entries) <= CHRONICLE_THRESHOLD:
        print("[INFO] Entry count (" + str(len(entries)) + ") <= " + str(CHRONICLE_THRESHOLD) + ". No action needed.")
        return 0

    print("\n[ACTION] Entry count (" + str(len(entries)) + ") > " + str(CHRONICLE_THRESHOLD) + ". Starting archive...")
    print()

    milestone = call_mimo_summarize(entries, config)
    print("\n[MILESTONE] " + milestone)

    spec_ok = append_milestone_to_spec(milestone, dry_run=dry_run)

    if not dry_run and spec_ok:
        new_content = clear_work_log(content)
        memory_path.write_text(new_content, encoding="utf-8")
        print("[MEMORY] Work log cleared in MEMORY.md (" + str(len(entries)) + " entries removed)")
    elif dry_run:
        print("[DRY-RUN] Would clear work log in MEMORY.md")

    print()
    print("=" * 55)
    print("Archive Chronicle Complete!")
    print("  Entries processed: " + str(len(entries)))
    print("  Milestone written: " + ("YES" if spec_ok else "NO"))
    print("  Memory pruned:     " + ("YES" if spec_ok and not dry_run else "DRY-RUN" if dry_run else "NO"))
    print("=" * 55)

    return 0


if __name__ == "__main__":
    sys.exit(main())
