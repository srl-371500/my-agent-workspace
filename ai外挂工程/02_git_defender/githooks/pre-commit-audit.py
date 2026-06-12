"""
Pre-commit audit script for AI Automation Project.
Runs before each commit to:
1. Check for sensitive information in ALL staged files
2. Validate Python syntax for all staged .py files
3. Run archive_chronicle.py for memory compression (if needed)
"""

import subprocess
import sys
import os
import re
import tempfile
from pathlib import Path

PYTHON_EXE = sys.executable

SKIP_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.svg',
    '.woff', '.woff2', '.ttf', '.eot', '.otf',
    '.zip', '.tar', '.gz', '.rar', '.7z',
    '.exe', '.dll', '.so', '.dylib',
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',
    '.pak', '.bin', '.dat', '.pb',
    '.mp3', '.mp4', '.wav', '.avi', '.mov',
}

SKIP_FILENAMES = {
    '.gitignore', '.gitattributes', '.editorconfig',
    'LICENSE', 'NOTICE', 'CHANGELOG',
}

SECRET_PATTERNS = [
    (r'sk-[a-zA-Z0-9_-]{20,}', "OpenAI/Anthropic-style API key"),
    (r'api[_-]?key\s*[:=]\s*["\'][^"\']{10,}', "API key assignment"),
    (r'secret[_-]?key\s*[:=]\s*["\'][^"\']{10,}', "Secret key assignment"),
    (r'password\s*[:=]\s*["\'][^"\']{8,}', "Password assignment"),
    (r'token\s*[:=]\s*["\'][a-zA-Z0-9_-]{20,}', "Token assignment"),
    (r'Bearer\s+[a-zA-Z0-9_-]{20,}', "Bearer token"),
    (r'LLM_API_KEY\s*=\s*["\'](?![\s]*your)[^"\']{10,}', "LLM API key"),
    (r'private[_-]?key\s*[:=]\s*["\'][^"\']{10,}', "Private key reference"),
]

PLACEHOLDER_PATTERNS = [
    "your_api_key_here",
    "your_actual_api_key_here",
    "REPLACE_WITH_YOUR_KEY",
    "sk-xxxxxxxx",
    "YOUR_API_KEY",
    "your-api-key-here",
    "placeholder",
    "example",
    "changeme",
]


def run_command(cmd):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1


def get_staged_files():
    stdout, _, rc = run_command("git diff --cached --name-only --diff-filter=ACM")
    if rc != 0:
        return []
    return [f for f in stdout.split('\n') if f.strip()]


def is_text_file(file_path):
    ext = Path(file_path).suffix.lower()
    if ext in SKIP_EXTENSIONS:
        return False
    name = Path(file_path).name
    if name in SKIP_FILENAMES:
        return False
    return True


def check_api_key():
    print("[1/3] Checking for sensitive information...")

    staged_files = get_staged_files()

    sensitive_config_files = ["config/settings.yaml", ".env"]
    staged_sensitive = [f for f in sensitive_config_files if f in staged_files]

    if staged_sensitive:
        print(f"  ! Sensitive config files staged: {', '.join(staged_sensitive)}")

        for file in staged_sensitive:
            print(f"  Scanning {file} for API keys...")

            stdout, stderr, rc = run_command(f"git show :{file}")
            if rc != 0:
                print(f"  X Error reading staged {file}: {stderr}")
                return False

            content = stdout

            has_placeholder = any(p in content for p in PLACEHOLDER_PATTERNS)
            if has_placeholder:
                print(f"  OK: {file} appears to contain placeholder values.")
                continue

            for pattern, desc in SECRET_PATTERNS:
                match = re.search(pattern, content)
                if match:
                    key_preview = match.group(0)[:20]
                    print()
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("  SECURITY ALERT: REAL API KEY DETECTED!")
                    print(f"  File: {file}")
                    print(f"  Type: {desc}")
                    print(f"  Preview: {key_preview}...")
                    print("  DO NOT commit this file with real API keys!")
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print()
                    return False

    all_text_files = [f for f in staged_files if is_text_file(f)]
    other_files = [f for f in all_text_files if f not in sensitive_config_files]

    if other_files:
        print(f"  Scanning {len(other_files)} staged file(s) for embedded secrets...")
        found_secrets = False

        for file in other_files:
            stdout, stderr, rc = run_command(f"git show :{file}")
            if rc != 0:
                continue

            for pattern, desc in SECRET_PATTERNS:
                match = re.search(pattern, stdout)
                if match:
                    has_placeholder = any(p.lower() in stdout.lower() for p in PLACEHOLDER_PATTERNS[:5])
                    if has_placeholder:
                        continue

                    key_preview = match.group(0)[:25]
                    print()
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("  SECURITY ALERT: EMBEDDED SECRET DETECTED!")
                    print(f"  File: {file}")
                    print(f"  Type: {desc}")
                    print(f"  Preview: {key_preview}...")
                    print("  Remove secrets before committing!")
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print()
                    found_secrets = True
                    break

            if found_secrets:
                return False

    print("  OK: No obvious secret patterns found.")
    return True


def check_python_syntax():
    print("[2/3] Checking Python syntax...")

    staged_files = get_staged_files()
    py_files = [f for f in staged_files if f.endswith('.py')]

    if not py_files:
        print("  - No Python files to check.")
        return True

    print(f"  Checking {len(py_files)} Python file(s)...")

    errors = 0

    for py_file in py_files:
        stdout, stderr, rc = run_command(f"git show :{py_file}")
        if rc != 0:
            print(f"  X {py_file} - Error reading staged content")
            errors += 1
            continue

        try:
            fd, temp_file = tempfile.mkstemp(suffix='.py')
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(stdout)

            _, compile_err, compile_rc = run_command(f'"{PYTHON_EXE}" -m py_compile "{temp_file}"')
            if compile_rc == 0:
                print(f"  OK: {py_file}")
            else:
                print(f"  X {py_file} - SYNTAX ERROR!")
                if compile_err:
                    print(f"     {compile_err}")
                errors += 1

            os.unlink(temp_file)
        except Exception as e:
            print(f"  X {py_file} - Error: {e}")
            errors += 1

    if errors > 0:
        print()
        print(f"  Found {errors} Python file(s) with syntax errors!")
        print("  Please fix the syntax errors before committing.")
        return False

    return True


def run_archive_chronicle():
    print("[3/3] Running memory chronicle archive...")

    hook_dir = Path(__file__).resolve().parent

    project_root = hook_dir.parent.parent.parent
    archive_script = project_root / "ai外挂工程" / "01_memory_core" / "archive_chronicle.py"
    if not archive_script.exists():
        archive_script = hook_dir.parent.parent / "01_memory_core" / "archive_chronicle.py"

    if not archive_script.exists():
        print(f"  - Archive script not found. Skipping.")
        return True

    try:
        _, stderr, rc = run_command(f'"{PYTHON_EXE}" "{archive_script}"')
        if rc == 0:
            print("  OK: Memory chronicle archive completed.")
        else:
            print(f"  ! Archive script exited with code {rc}")
            if stderr:
                print(f"    {stderr}")
        return True
    except Exception as e:
        print(f"  ! Archive script error (non-blocking): {e}")
        return True


def main():
    print("=" * 50)
    print("Pre-commit Audit Hook")
    print("=" * 50)

    staged_files = get_staged_files()
    if not staged_files:
        print("No staged files to check.")
        sys.exit(0)

    print(f"Staged files: {len(staged_files)}")
    for f in staged_files:
        print(f"  - {f}")
    print()

    checks_passed = True

    if not check_api_key():
        checks_passed = False

    print()

    if not check_python_syntax():
        checks_passed = False

    print()

    if checks_passed:
        run_archive_chronicle()

    print()
    print("=" * 50)

    if checks_passed:
        print("Pre-commit audit PASSED!")
        sys.exit(0)
    else:
        print("Pre-commit audit FAILED! Commit blocked.")
        sys.exit(1)


if __name__ == "__main__":
    main()
