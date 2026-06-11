"""
Archive Memory Script - Hardcoded Memory Management
Automatically archives old memory entries when count exceeds threshold
Prevents memory bloat and maintains clean CHRONICLE.md
"""

import re
import os
from pathlib import Path
from datetime import datetime
from typing import List, Tuple


MEMORY_ROOT = Path(__file__).resolve().parent
CHRONICLE_PATH = MEMORY_ROOT / "CHRONICLE.md"
SPEC_PATH = MEMORY_ROOT / "SPEC.md"
ARCHIVE_DIR = MEMORY_ROOT / "archive"

MAX_ACTIVE_ENTRIES = 5
ARCHIVE_COUNT = 3


def parse_chronicle_entries(content: str) -> List[Tuple[str, str]]:
    """Parse CHRONICLE.md and extract task entries
    
    Supports both English and Chinese headers:
    - Entry section: '## Activity Task Window', '## Activity Tasks', '## 活动任务窗口', '## 活动任务'
    - Entry items: '### Task #N', '### 任务 #N', or any '### ' header
    - Section end: any '## ' header (not '### ')
    """
    entries = []
    current_entry = []
    current_header = ""
    
    in_active_section = False
    reached_end = False
    
    entry_section_keywords = [
        '## Activity Task Window',
        '## Activity Tasks',
        '## 活动任务窗口',
        '## 活动任务',
    ]
    
    for line in content.split('\n'):
        if reached_end:
            break
            
        if any(keyword in line for keyword in entry_section_keywords):
            in_active_section = True
            continue
        
        if in_active_section and line.startswith('### '):
            if current_header and current_entry:
                entries.append((current_header, '\n'.join(current_entry)))
            current_header = line
            current_entry = []
        elif in_active_section and current_header:
            if line.startswith('## ') and not line.startswith('### '):
                if current_header and current_entry:
                    entries.append((current_header, '\n'.join(current_entry)))
                reached_end = True
                continue
            current_entry.append(line)
    
    if not reached_end and current_header and current_entry:
        entries.append((current_header, '\n'.join(current_entry)))
    
    return entries


def create_archive_filename() -> str:
    """Create archive filename based on current date"""
    now = datetime.now()
    return f"mem_{now.strftime('%Y_%m')}.md"


def archive_old_entries(entries: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """Split entries into active and archive"""
    if len(entries) <= MAX_ACTIVE_ENTRIES:
        return entries, []
    
    archive_entries = entries[:ARCHIVE_COUNT]
    active_entries = entries[ARCHIVE_COUNT:]
    
    return active_entries, archive_entries


def create_summary(entry_header: str, entry_content: str) -> str:
    """Create a summary of an entry for SPEC.md"""
    lines = entry_content.strip().split('\n')
    
    status = ""
    content_summary = ""
    
    for line in lines:
        if line.strip().startswith('- **Status**:'):
            status = line.strip().replace('- **Status**:', '').strip()
        elif line.strip().startswith('- **Content**:'):
            content_summary = line.strip().replace('- **Content**:', '').strip()
    
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', entry_header)
    date_str = date_match.group(1) if date_match else "Unknown"
    
    title = entry_header.replace('###', '').strip()
    title = re.sub(r'\*\*.*?\*\*:?', '', title).strip()
    title = title.split('-')[0].strip() if '-' in title else title
    
    return f"- **{date_str}**: {title} ({status})"


def append_to_spec(summaries: List[str]) -> None:
    """Append summaries to SPEC.md"""
    if not SPEC_PATH.exists():
        print(f"[WARNING] SPEC.md not found at {SPEC_PATH}")
        return
    
    content = SPEC_PATH.read_text(encoding='utf-8')
    
    archive_marker = "## Historical Milestones"
    if archive_marker not in content:
        content += f"\n\n{archive_marker}\n\n"
    
    archive_section = f"\n### Archived on {datetime.now().strftime('%Y-%m-%d')}\n"
    for summary in summaries:
        archive_section += f"{summary}\n"
    
    content += archive_section
    SPEC_PATH.write_text(content, encoding='utf-8')
    print(f"[SUCCESS] Added {len(summaries)} summaries to SPEC.md")


def save_archive(entries: List[Tuple[str, str]]) -> None:
    """Save archived entries to monthly file"""
    ARCHIVE_DIR.mkdir(exist_ok=True)
    
    archive_file = ARCHIVE_DIR / create_archive_filename()
    
    archive_content = ""
    if archive_file.exists():
        archive_content = archive_file.read_text(encoding='utf-8')
    else:
        archive_content = f"# Memory Archive - {datetime.now().strftime('%Y-%m')}\n\n"
    
    archive_content += f"\n---\n## Archived on {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    
    for header, content in entries:
        archive_content += f"{header}\n{content}\n\n"
    
    archive_file.write_text(archive_content, encoding='utf-8')
    print(f"[SUCCESS] Archived {len(entries)} entries to {archive_file.name}")


def rebuild_chronicle(active_entries: List[Tuple[str, str]], full_content: str) -> None:
    """Rebuild CHRONICLE.md with only active entries"""
    lines = full_content.split('\n')
    
    new_lines = []
    in_active_section = False
    skip_until_next_section = False
    
    for line in lines:
        if '## Activity Task Window' in line or '## Activity Tasks' in line:
            new_lines.append(line)
            new_lines.append("")
            in_active_section = True
            skip_until_next_section = False
            
            for header, content in active_entries:
                new_lines.append(header)
                new_lines.append(content)
                new_lines.append("")
            
            continue
        
        if in_active_section:
            if line.startswith('## ') and not line.startswith('### '):
                in_active_section = False
                new_lines.append(line)
            continue
        
        new_lines.append(line)
    
    stats_section = False
    for i, line in enumerate(new_lines):
        if '## Task Statistics' in line or '## Statistics' in line:
            stats_section = True
        if stats_section and 'Active tasks:' in line:
            new_lines[i] = f"  Active tasks: {len(active_entries)}"
        if stats_section and 'Archived tasks:' in line:
            new_lines[i] = f"  Archived tasks: {ARCHIVE_COUNT}"
        if stats_section and 'Archive threshold:' in line:
            new_lines[i] = f"  Archive threshold: {MAX_ACTIVE_ENTRIES}"
    
    CHRONICLE_PATH.write_text('\n'.join(new_lines), encoding='utf-8')
    print(f"[SUCCESS] Rebuilt CHRONICLE.md with {len(active_entries)} active entries")


def main():
    print("=" * 60)
    print("Archive Memory Script")
    print("=" * 60)
    print(f"Memory root: {MEMORY_ROOT}")
    print(f"Max active entries: {MAX_ACTIVE_ENTRIES}")
    print(f"Archive count: {ARCHIVE_COUNT}")
    print()
    
    if not CHRONICLE_PATH.exists():
        print("[INFO] CHRONICLE.md not found. Nothing to archive.")
        return
    
    content = CHRONICLE_PATH.read_text(encoding='utf-8')
    entries = parse_chronicle_entries(content)
    
    print(f"[INFO] Found {len(entries)} entries in CHRONICLE.md")
    
    if len(entries) <= MAX_ACTIVE_ENTRIES:
        print(f"[INFO] Entry count ({len(entries)}) <= threshold ({MAX_ACTIVE_ENTRIES}). No archiving needed.")
        return
    
    print(f"[ACTION] Entry count ({len(entries)}) > threshold ({MAX_ACTIVE_ENTRIES}). Starting archiving...")
    
    active_entries, archive_entries = archive_old_entries(entries)
    
    summaries = []
    for header, content in archive_entries:
        summary = create_summary(header, content)
        summaries.append(summary)
    
    append_to_spec(summaries)
    save_archive(archive_entries)
    rebuild_chronicle(active_entries, content)
    
    print()
    print("=" * 60)
    print("Archive completed!")
    print(f"  Archived: {len(archive_entries)} entries")
    print(f"  Active: {len(active_entries)} entries")
    print("=" * 60)


if __name__ == "__main__":
    main()