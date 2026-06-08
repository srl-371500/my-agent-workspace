"""
Pre-commit audit script for AI Automation Project.
Runs before each commit to:
1. Check for sensitive information in config/settings.yaml
2. Validate Python syntax for all staged .py files
"""

import subprocess
import sys
import os
import re
import tempfile


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


def check_api_key():
    print("[1/2] Checking for sensitive information...")
    
    staged_files = get_staged_files()
    
    if "config/settings.yaml" not in staged_files:
        print("  - config/settings.yaml not staged. Skipping key check.")
        return True
    
    print("  ! config/settings.yaml is staged. Scanning for API keys...")
    
    stdout, stderr, rc = run_command("git show :config/settings.yaml")
    if rc != 0:
        print(f"  X Error reading staged settings.yaml: {stderr}")
        return False
    
    content = stdout
    
    placeholder_patterns = [
        "your_api_key_here",
        "your_actual_api_key_here",
        "REPLACE_WITH_YOUR_KEY",
        "sk-xxxxxxxx",
        "YOUR_API_KEY",
    ]
    
    for pattern in placeholder_patterns:
        if pattern in content:
            print("  OK: API key appears to be a placeholder.")
            return True
    
    api_key_match = re.search(r'api_key:\s*["\']?([^"\'\n]+)["\']?', content)
    if api_key_match:
        api_key_value = api_key_match.group(1).strip()
        
        if len(api_key_value) > 10 and re.search(r'[a-zA-Z0-9]{10,}', api_key_value):
            print()
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("  SECURITY ALERT: REAL API KEY DETECTED!")
            print("  File: config/settings.yaml")
            print(f"  Key preview: {api_key_value[:10]}...")
            print("  DO NOT commit this file with real API keys!")
            print("  Use a placeholder value instead.")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print()
            return False
    
    print("  OK: No obvious API key patterns found.")
    return True


def check_python_syntax():
    print("[2/2] Checking Python syntax...")
    
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
            
            _, compile_err, compile_rc = run_command(f'py -m py_compile "{temp_file}"')
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
    print("=" * 50)
    
    if checks_passed:
        print("Pre-commit audit PASSED!")
        sys.exit(0)
    else:
        print("Pre-commit audit FAILED! Commit blocked.")
        sys.exit(1)


if __name__ == "__main__":
    main()