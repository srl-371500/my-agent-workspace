# Project Rules — Agent Sandbox Toolkit

## Architecture
- Source: src/
- Docs: docs/
- Tests: tests/

## Development
- Memory Core: src/01_memory_core/
- Git Defender: src/02_git_defender/githooks/

## Testing
- `python -m py_compile src/01_memory_core/utils.py`
- `python -m py_compile src/01_memory_core/archive_chronicle.py`
- `python -m py_compile src/02_git_defender/githooks/pre-commit-audit.py`

## Memory Management
- MEMORY.md is the active log. When entries > 5, run:
  `python src/01_memory_core/archive_chronicle.py`
- LLM summarization requires .env with LLM_API_KEY configured.
