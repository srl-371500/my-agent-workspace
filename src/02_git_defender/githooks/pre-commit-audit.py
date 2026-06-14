# -*- coding: utf-8 -*-
import subprocess, sys, os, re, tempfile, importlib.util
from pathlib import Path
PY = sys.executable
SKIP = {'.png','.jpg','.jpeg','.gif','.webp','.ico','.svg','.woff','.woff2','.ttf','.eot',
    '.otf','.zip','.tar','.gz','.rar','.7z','.exe','.dll','.so','.dylib','.pdf','.doc',
    '.docx','.xls','.xlsx','.pak','.bin','.dat','.pb','.mp3','.mp4','.wav'}
SECRETS = [(r'sk-[a-zA-Z0-9_-]{20,}',"API key"),(r'api[_-]?key\s*[:=]\s*["\'][^"\']{10,}',"API key"),
    (r'secret[_-]?key\s*[:=]\s*["\'][^"\']{10,}',"Secret"),(r'password\s*[:=]\s*["\'][^"\']{8,}',"Password"),
    (r'token\s*[:=]\s*["\'][a-zA-Z0-9_-]{20,}',"Token"),(r'Bearer\s+[a-zA-Z0-9_-]{20,}',"Bearer"),
    (r'LLM_API_KEY\s*=\s*["\'](?![\s]*your)[^"\']{10,}',"LLM key"),
    (r'private[_-]?key\s*[:=]\s*["\'][^"\']{10,}',"Private key")]
SAFE = ["your_api_key_here","your_actual_api_key_here","REPLACE_WITH_YOUR_KEY",
    "sk-xxxxxxxx","YOUR_API_KEY","your-api-key-here","placeholder","example","changeme"]

def run(cmd):
    try:
        r = subprocess.run(cmd,shell=True,capture_output=True,text=True,check=False)
        return r.stdout.strip(),r.stderr.strip(),r.returncode
    except Exception as e: return "",str(e),1

def staged():
    o,_,rc = run("git diff --cached --name-only --diff-filter=ACM")
    return [f for f in o.split('\n') if f.strip()] if rc==0 else []

def is_bin(fp):
    return Path(fp).suffix.lower() in SKIP or Path(fp).name in {'.gitignore','.gitattributes','.editorconfig','LICENSE'}

def check_secrets():
    print("[1/4] Secrets scan...")
    for f in staged():
        if is_bin(f): continue
        o,_,rc = run(f"git show :{f}")
        if rc!=0 or any(p in o for p in SAFE): continue
        for pat,desc in SECRETS:
            m = re.search(pat,o)
            if m: print(f"\n  ALERT: {desc} in {f}: {m.group(0)[:25]}...\n  BLOCKED.\n"); return False
    print("  OK"); return True

def check_syntax():
    print("[2/4] Python syntax...")
    py = [f for f in staged() if f.endswith('.py')]
    if not py: print("  - skip"); return True
    errs = 0
    for f in py:
        o,_,rc = run(f"git show :{f}")
        if rc!=0: errs+=1; continue
        fd,tmp = tempfile.mkstemp(suffix='.py')
        with os.fdopen(fd,'w',encoding='utf-8') as fh: fh.write(o)
        _,e,crc = run(f'"{PY}" -m py_compile "{tmp}"')
        if crc!=0: print(f"  X {f}: {e}"); errs+=1
        os.unlink(tmp)
    if errs: print(f"  {errs} error(s)"); return False
    print("  OK"); return True

def _utils():
    hd = Path(__file__).resolve().parent
    for c in [hd.parent.parent/"01_memory_core"/"utils.py", hd.parent.parent.parent/"ai外挂工程"/"01_memory_core"/"utils.py"]:
        if c.exists():
            s = importlib.util.spec_from_file_location("utils",str(c))
            m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
    return None

def check_anim():
    print("[3/4] Animation analysis...")
    htmls = [f for f in staged() if f.endswith(('.html','.htm'))]
    if not htmls: print("  - skip"); return True
    u = _utils()
    if not u: print("  - utils not found"); return True
    for f in htmls:
        o,_,rc = run(f"git show :{f}")
        if rc!=0: continue
        fd,tmp = tempfile.mkstemp(suffix='.html')
        with os.fdopen(fd,'w',encoding='utf-8') as fh: fh.write(o)
        print(f"  {f}: {u.summarize_animations(u.extract_animations(tmp))}"); os.unlink(tmp)
    print("  OK"); return True

def run_archive():
    print("[4/4] Archive chronicle...")
    hd = Path(__file__).resolve().parent
    for p in [hd.parent.parent/"01_memory_core"/"archive_chronicle.py", hd.parent.parent.parent/"ai外挂工程"/"01_memory_core"/"archive_chronicle.py"]:
        if p.exists():
            _,e,rc = run(f'"{PY}" "{p}"')
            if rc!=0 and e: print(f"  ! {e}")
            else: print("  OK")
            return
    print("  - not found")

def main():
    print("="*50+"\nPre-commit Audit\n"+"="*50)
    if not staged(): sys.exit(0)
    ok = check_secrets(); print()
    ok = check_syntax() and ok; print()
    check_anim(); print()
    if ok: run_archive()
    print("="*50); sys.exit(0 if ok else 1)

if __name__ == "__main__": main()
