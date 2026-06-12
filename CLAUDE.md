# Project Rules 鈥?Agent Sandbox Toolkit

## Development
- Toolkit: ai外挂工程/
- Memory Core: ai外挂工程/01_memory_core/
- Git Defender: ai外挂工程/02_git_defender/githooks/

## Testing
- `python -m py_compile ai外挂工程/01_memory_core/utils.py`
- `python -m py_compile ai外挂工程/01_memory_core/archive_chronicle.py`
- `python -m py_compile ai外挂工程/02_git_defender/githooks/pre-commit-audit.py`

## Memory Management
- MEMORY.md is the active log. When entries > 5, run:
  `python ai澶栨寕宸ョ▼/01_memory_core/archive_chronicle.py`
- LLM summarization requires .env with LLM_API_KEY configured.
