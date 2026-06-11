"""
通用配置加载器 - 支持环境变量优先，YAML 配置回退
Zero-Secrets 架构：所有敏感信息必须通过环境变量注入
D-Drive Absolute Isolation: All paths resolved from __file__
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv


WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
ENV_PATH = WORKSPACE_ROOT / ".env"


class LLMConfig(BaseModel):
    """LLM 模型配置"""
    model: str = Field(default="mimo-v2.5", description="模型名称")
    api_key: str = Field(..., description="API 密钥")
    base_url: str = Field(..., description="API 端点")


class BrowserConfig(BaseModel):
    """浏览器配置"""
    type: str = Field(default="chromium", description="浏览器类型")
    headless: bool = Field(default=True, description="无头模式")
    viewport_width: int = Field(default=1920, description="视口宽度")
    viewport_height: int = Field(default=1080, description="视口高度")


class AppConfig(BaseModel):
    """应用配置"""
    llm: LLMConfig
    browser: BrowserConfig
    log_level: str = Field(default="INFO", description="日志级别")


def load_env_file(env_path: Optional[Path] = None) -> None:
    """加载 .env 文件（基于 __file__ 绝对路径定位）"""
    if env_path is None:
        env_path = ENV_PATH
    
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
        print(f"[SUCCESS] Loaded .env from: {env_path}")
    else:
        print(f"[WARNING] .env not found at: {env_path}")
        print(f"Please copy .env.example to .env and fill in your API key.")


def get_llm_config() -> LLMConfig:
    """获取 LLM 配置（环境变量优先）"""
    load_env_file()
    
    model = os.getenv("LLM_MODEL", "mimo-v2.5")
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    
    if not api_key:
        raise ValueError(
            "LLM_API_KEY 环境变量未设置！\n"
            "请复制 .env.example 为 .env 并填入你的 API 密钥。\n"
            "或设置系统环境变量：export LLM_API_KEY='your-key'"
        )
    
    if not base_url:
        raise ValueError(
            "LLM_BASE_URL 环境变量未设置！\n"
            "请复制 .env.example 为 .env 并填入 API 端点。\n"
            "或设置系统环境变量：export LLM_BASE_URL='https://api.example.com/v1'"
        )
    
    return LLMConfig(
        model=model,
        api_key=api_key,
        base_url=base_url
    )


def get_browser_config() -> BrowserConfig:
    """获取浏览器配置"""
    return BrowserConfig(
        type=os.getenv("BROWSER_TYPE", "chromium"),
        headless=os.getenv("BROWSER_HEADLESS", "true").lower() == "true",
        viewport_width=int(os.getenv("BROWSER_VIEWPORT_WIDTH", "1920")),
        viewport_height=int(os.getenv("BROWSER_VIEWPORT_HEIGHT", "1080"))
    )


def get_app_config() -> AppConfig:
    """获取完整应用配置"""
    return AppConfig(
        llm=get_llm_config(),
        browser=get_browser_config(),
        log_level=os.getenv("LOG_LEVEL", "INFO")
    )


def validate_api_key_masked(api_key: str) -> str:
    """验证并掩码 API 密钥（用于日志输出）"""
    if len(api_key) > 10:
        return f"{api_key[:6]}...{api_key[-4:]}"
    return "***"


if __name__ == "__main__":
    try:
        config = get_app_config()
        print("=" * 60)
        print("配置加载测试")
        print("=" * 60)
        print(f"  LLM Model: {config.llm.model}")
        print(f"  LLM Base URL: {config.llm.base_url}")
        print(f"  LLM API Key: {validate_api_key_masked(config.llm.api_key)}")
        print(f"  Browser: {config.browser.type} (headless={config.browser.headless})")
        print(f"  Log Level: {config.log_level}")
        print("=" * 60)
        print("[√] 配置加载成功！")
    except Exception as e:
        print(f"[✗] 配置加载失败: {e}")