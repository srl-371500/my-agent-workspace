import json
import os
from datetime import datetime
from pathlib import Path


CRAWLER_ROOT = Path(__file__).resolve().parents[2]
COST_RULES_PATH = CRAWLER_ROOT / "config" / "cost_rules.json"
DEFAULT_AUDIT_LOG = CRAWLER_ROOT / "logs" / "cost_audit.json"


def load_cost_rules():
    with open(COST_RULES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def calculate_cost(prompt_tokens, completion_tokens, model="mimo-v2.5"):
    rules = load_cost_rules()
    model_config = rules["models"].get(model)
    if not model_config:
        raise ValueError(f"Unknown model: {model}")
    
    pricing = model_config["pricing"]
    prompt_cost_cny = (prompt_tokens / 1_000_000) * pricing["prompt_tokens_per_million_cny"]
    completion_cost_cny = (completion_tokens / 1_000_000) * pricing["completion_tokens_per_million_cny"]
    total_cost_cny = prompt_cost_cny + completion_cost_cny
    
    prompt_cost_usd = (prompt_tokens / 1_000_000) * pricing["prompt_tokens_per_million_usd"]
    completion_cost_usd = (completion_tokens / 1_000_000) * pricing["completion_tokens_per_million_usd"]
    total_cost_usd = prompt_cost_usd + completion_cost_usd
    
    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "cost_cny": round(total_cost_cny, 6),
        "cost_usd": round(total_cost_usd, 6),
        "prompt_cost_cny": round(prompt_cost_cny, 6),
        "completion_cost_cny": round(completion_cost_cny, 6),
    }


def record_audit(task_name, usage_data, audit_log_path=None):
    if audit_log_path is None:
        audit_log_path = DEFAULT_AUDIT_LOG
    
    audit_log_path = Path(audit_log_path)
    audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    
    if audit_log_path.exists():
        with open(audit_log_path, "r", encoding="utf-8") as f:
            records = json.load(f)
    else:
        records = []
    
    prompt_tokens = usage_data.get("prompt_tokens", 0)
    completion_tokens = usage_data.get("completion_tokens", 0)
    
    cost_info = calculate_cost(prompt_tokens, completion_tokens)
    
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "task": task_name,
        "model": "mimo-v2.5",
        "tokens_used": cost_info["total_tokens"],
        "prompt_tokens": cost_info["prompt_tokens"],
        "completion_tokens": cost_info["completion_tokens"],
        "cost_cny": cost_info["cost_cny"],
        "cost_usd": cost_info["cost_usd"],
        "prompt_cost_cny": cost_info["prompt_cost_cny"],
        "completion_cost_cny": cost_info["completion_cost_cny"],
    }
    
    records.append(record)
    
    with open(audit_log_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    
    return record


def print_cost_summary(record):
    print(f"  Tokens: {record['tokens_used']} (prompt: {record['prompt_tokens']}, completion: {record['completion_tokens']})")
    print(f"  Cost: ¥{record['cost_cny']:.6f} CNY / ${record['cost_usd']:.6f} USD")
    print(f"  Breakdown: prompt ¥{record['prompt_cost_cny']:.6f} + completion ¥{record['completion_cost_cny']:.6f}")