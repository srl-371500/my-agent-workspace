"""
自愈式、无选择器多模态数据蒸馏爬虫
彻底抛弃 CSS 选择器，使用 Markdown 降维 + Pydantic 结构化输出
"""

import asyncio
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from config_loader import get_llm_config, get_browser_config, validate_api_key_masked
from inspiration_schema import InspirationSchema, get_extraction_prompt, get_self_healing_prompt
from html_to_markdown import html_to_markdown, extract_meta_info

os.environ['BROWSER_USE_DISABLE_EXTENSIONS'] = 'true'

from playwright.async_api import async_playwright
from openai import AsyncOpenAI
from cost_audit import record_audit, print_cost_summary, calculate_cost, DEFAULT_AUDIT_LOG


PORTFOLIO_URLS = [
    {
        "url": "https://jesperlandberg.se/",
        "focus": "smooth scroll 滚动效果和文字图片动效"
    },
    {
        "url": "https://robinmastromarino.com/",
        "focus": "页面转场效果和 slider 交互"
    },
]


async def fetch_page_content(url: str, timeout: int = 30000) -> Optional[str]:
    """
    使用 Playwright 获取网页 HTML 内容
    
    Args:
        url: 网页 URL
        timeout: 超时时间（毫秒）
    
    Returns:
        HTML 内容或 None
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            await page.goto(url, wait_until='networkidle', timeout=timeout)
            await page.wait_for_timeout(2000)
            
            html_content = await page.content()
            
            await browser.close()
            return html_content
            
    except Exception as e:
        print(f"  [✗] 页面获取失败: {e}")
        return None


async def extract_with_llm(
    client: AsyncOpenAI,
    model: str,
    markdown_content: str,
    site_url: str,
    max_retries: int = 2
) -> Optional[InspirationSchema]:
    """
    使用 LLM 进行结构化提取，支持自愈重试
    
    Args:
        client: OpenAI 客户端
        model: 模型名称
        markdown_content: Markdown 内容
        site_url: 网站 URL
        max_retries: 最大重试次数
    
    Returns:
        InspirationSchema 或 None
    """
    for attempt in range(max_retries + 1):
        try:
            if attempt == 0:
                prompt = get_extraction_prompt(markdown_content, site_url)
            else:
                prompt = get_self_healing_prompt(
                    error_message=str(last_error),
                    markdown_content=markdown_content,
                    site_url=site_url
                )
            
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的前端设计师和创意总监，擅长分析网页设计。请严格按照 JSON Schema 输出分析结果。"},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)
            
            schema = InspirationSchema(**result_json)
            
            usage = response.usage
            usage_data = {
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0
            }
            
            return schema, usage_data
            
        except Exception as e:
            last_error = e
            if attempt < max_retries:
                print(f"  [!] 提取失败，正在自愈重试 ({attempt + 1}/{max_retries})...")
                await asyncio.sleep(1)
            else:
                print(f"  [✗] 提取失败，已达最大重试次数: {e}")
                return None, {"prompt_tokens": 0, "completion_tokens": 0}


async def analyze_portfolio(site_info: Dict[str, str], llm_config) -> tuple:
    """
    分析单个作品集网站（无选择器版本）
    
    Args:
        site_info: 网站信息字典
        llm_config: LLM 配置
    
    Returns:
        (分析结果, 使用数据)
    """
    url = site_info["url"]
    focus = site_info["focus"]
    
    print(f"  [1/4] 获取页面内容...")
    html_content = await fetch_page_content(url)
    if not html_content:
        return "页面获取失败", {"prompt_tokens": 0, "completion_tokens": 0}
    
    print(f"  [2/4] HTML → Markdown 降维...")
    markdown_content = html_to_markdown(html_content, url)
    meta_info = extract_meta_info(html_content)
    
    print(f"  [3/4] LLM 结构化提取...")
    client = AsyncOpenAI(
        api_key=llm_config.api_key,
        base_url=llm_config.base_url
    )
    
    extraction_result, usage_data = await extract_with_llm(
        client=client,
        model=llm_config.model,
        markdown_content=markdown_content,
        site_url=url
    )
    
    if extraction_result:
        print(f"  [4/4] 生成分析报告...")
        report = format_structured_report(extraction_result, meta_info, focus)
        return report, usage_data
    else:
        print(f"  [4/4] 回退到原始分析...")
        report = f"## {url}\n\n**分析重点**: {focus}\n\n**原始内容摘要**:\n{markdown_content[:2000]}...\n\n**元信息**:\n- 标题: {meta_info.get('title', 'N/A')}\n- 描述: {meta_info.get('description', 'N/A')}"
        return report, usage_data


def format_structured_report(
    schema: InspirationSchema,
    meta_info: dict,
    focus: str
) -> str:
    """
    格式化结构化报告
    
    Args:
        schema: 灵感分析 Schema
        meta_info: 网页元信息
        focus: 分析重点
    
    Returns:
        Markdown 格式的报告
    """
    report = f"""## {schema.site_name}

**分析重点**: {focus}

### 核心视觉风格
{schema.core_style}

### 配色方案
{''.join([f'`{color}` ' for color in schema.color_palette])}

### 字体排版
{schema.typography}

### 布局模式
{schema.layout_pattern}

### 动画技术
**类型**: {', '.join(schema.animation_types)}

**实现细节**:
{schema.animation_details}

### 技术栈
{', '.join(schema.tech_stack)}

### 交互特性
{''.join([f'- {feature}\n' for feature in schema.interactive_features])}

### 关键灵感
{''.join([f'- {inspiration}\n' for inspiration in schema.key_inspirations])}

### 可复用模式
{''.join([f'- {pattern}\n' for pattern in schema.reusable_patterns])}

### 实现建议
{''.join([f'- {tip}\n' for tip in schema.implementation_tips])}

### 创意评分
{'⭐' * schema.overall_score} ({schema.overall_score}/10)

---
"""
    return report


def generate_report(analyses: List[tuple]) -> str:
    """生成完整报告"""
    report = f"""# 作品集灵感分析报告 (Portfolio Inspiration Report)

> 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} (Asia/Shanghai)
> 分析引擎: Playwright + Markdown 降维 + LLM 结构化提取
> 特性: 无 CSS 选择器，自愈式提取

---

## 执行摘要

本报告分析了 {len(analyses)} 个精选个人作品集网站，提取创意灵感和技术实现方案。

---

"""
    
    for i, (site_info, analysis, usage) in enumerate(analyses, 1):
        report += analysis
    
    report += """## 总结与技术建议

### 设计趋势
- 极简布局配合大胆排版
- 深色模式作为默认，强调色点缀
- 充足留白和非对称构图
- 自定义鼠标交互增强参与感

### 动效模式
- 滚动触发的渐显动画，配合错开时序
- 使用 GSAP 或 Framer Motion 实现平滑页面转场
- 3D 元素和视差效果增加深度感
- 悬停和点击状态的微交互

### 技术推荐
- **GSAP**: 复杂时间线动画的行业标准
- **Three.js**: 沉浸式 3D 网页体验
- **Framer Motion**: React 原生动画库
- **Locomotive Scroll**: 带视差的平滑滚动

### 实现要点
- 使用 `Intersection Observer API` 实现滚动触发动画
- 使用 `requestAnimationFrame` 实现 60fps 流畅动画
- 考虑使用 `will-change` CSS 属性优化性能
- 使用 CSS 自定义属性实现动态主题切换

---

*报告由 AI Browser Distillation Service 自动生成*
*采用无选择器架构，防止网页改版导致代码失效*
"""
    
    return report


async def main():
    print("=" * 60)
    print("作品集灵感分析 (Portfolio Inspiration Analysis)")
    print("=" * 60)
    print("架构: 无选择器 + Markdown 降维 + Pydantic 结构化输出")
    print("=" * 60)
    
    print("\n[加载配置]")
    try:
        llm_config = get_llm_config()
        browser_config = get_browser_config()
    except ValueError as e:
        print(f"[✗] 配置加载失败: {e}")
        return
    
    print(f"  LLM Model: {llm_config.model}")
    print(f"  LLM Base URL: {llm_config.base_url}")
    print(f"  LLM API Key: {validate_api_key_masked(llm_config.api_key)}")
    print(f"  Browser: {browser_config.type} (headless={browser_config.headless})")
    
    print(f"\n[分析目标]")
    for site in PORTFOLIO_URLS:
        print(f"  - {site['url']}")
        print(f"    重点: {site['focus']}")
    
    analyses = []
    total_prompt_tokens = 0
    total_completion_tokens = 0
    
    for site_info in PORTFOLIO_URLS:
        url = site_info["url"]
        print(f"\n{'=' * 60}")
        print(f"正在分析: {url}")
        print(f"分析重点: {site_info['focus']}")
        print("-" * 60)
        
        try:
            result, usage_data = await analyze_portfolio(site_info, llm_config)
            analyses.append((site_info, result, usage_data))
            total_prompt_tokens += usage_data["prompt_tokens"]
            total_completion_tokens += usage_data["completion_tokens"]
            
            print(f"✓ 分析完成: {url}")
            print(f"  本次 Token 消耗: prompt={usage_data['prompt_tokens']}, completion={usage_data['completion_tokens']}")
            
            cost_record = record_audit(
                task_name=f"portfolio_distill_{url}",
                usage_data=usage_data,
            )
            print(f"  成本审计:")
            print_cost_summary(cost_record)
            
        except Exception as e:
            print(f"✗ 分析失败: {url}")
            print(f"  错误: {str(e)}")
            analyses.append((site_info, f"分析失败: {str(e)}", {"prompt_tokens": 0, "completion_tokens": 0}))
    
    print(f"\n{'=' * 60}")
    print("生成报告...")
    
    report = generate_report(analyses)
    
    crawler_root = Path(__file__).resolve().parents[2]
    report_path = crawler_root / "reports" / "portfolio_inspiration_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\n✓ 报告已保存: {report_path}")
    
    total_cost = calculate_cost(total_prompt_tokens, total_completion_tokens)
    summary_record = record_audit(
        task_name="portfolio_distill_total",
        usage_data={"prompt_tokens": total_prompt_tokens, "completion_tokens": total_completion_tokens},
    )
    
    print(f"\n{'=' * 60}")
    print("Token 审计汇总 (Cost Audit Summary)")
    print("=" * 60)
    print(f"  总 Token 消耗: {total_cost['total_tokens']}")
    print(f"  Prompt Tokens: {total_cost['prompt_tokens']}")
    print(f"  Completion Tokens: {total_cost['completion_tokens']}")
    print(f"  总成本: ¥{total_cost['cost_cny']:.6f} CNY / ${total_cost['cost_usd']:.6f} USD")
    print(f"\n✓ 审计日志已保存: {DEFAULT_AUDIT_LOG}")
    print(f"\n分析完成: 共 {len(analyses)} 个网站")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())