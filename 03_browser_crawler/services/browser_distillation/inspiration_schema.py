"""
灵感分析结构化输出 Schema
使用 Pydantic 约束 LLM 输出格式，实现自愈式提取
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class AnimationType(str, Enum):
    """动画类型枚举"""
    SCROLL_TRIGGERED = "scroll_triggered"
    HOVER_EFFECT = "hover_effect"
    PAGE_TRANSITION = "page_transition"
    PARALLAX = "parallax"
    THREE_D = "three_d"
    LOADING = "loading"
    CURSOR_FOLLOW = "cursor_follow"
    MICRO_INTERACTION = "micro_interaction"


class TechStack(str, Enum):
    """技术栈枚举"""
    GSAP = "gsap"
    THREE_JS = "three_js"
    FRAMER_MOTION = "framer_motion"
    LOCOMOTIVE_SCROLL = "locomotive_scroll"
    SWIPER = "swiper"
    LENIS = "lenis"
    MOTION = "motion"
    OTHER = "other"


class InspirationSchema(BaseModel):
    """灵感分析结构化输出 Schema"""
    
    site_name: str = Field(
        description="网站名称或域名"
    )
    
    core_style: str = Field(
        description="核心视觉风格描述，包括配色、排版、布局特点"
    )
    
    color_palette: List[str] = Field(
        description="主要颜色列表，使用 HEX 格式",
        min_items=2,
        max_items=6
    )
    
    typography: str = Field(
        description="字体排版风格描述"
    )
    
    layout_pattern: str = Field(
        description="布局模式描述，如网格系统、间距、构图"
    )
    
    animation_types: List[AnimationType] = Field(
        description="使用的主要动画类型",
        min_items=1
    )
    
    animation_details: str = Field(
        description="动画实现细节描述"
    )
    
    tech_stack: List[TechStack] = Field(
        description="猜测使用的技术栈",
        min_items=1
    )
    
    interactive_features: List[str] = Field(
        description="交互特性列表",
        min_items=1,
        max_items=5
    )
    
    key_inspirations: List[str] = Field(
        description="关键灵感点列表",
        min_items=1,
        max_items=5
    )
    
    reusable_patterns: List[str] = Field(
        description="可复用的设计模式列表",
        min_items=1,
        max_items=5
    )
    
    implementation_tips: List[str] = Field(
        description="实现建议列表",
        min_items=1,
        max_items=5
    )
    
    overall_score: int = Field(
        description="整体创意评分 (1-10)",
        ge=1,
        le=10
    )
    
    class Config:
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "site_name": "jesperlandberg.se",
                "core_style": "极简主义深色主题，大胆的排版，充足的留白",
                "color_palette": ["#000000", "#ffffff", "#ff4444"],
                "typography": "无衬线字体，大字号标题，层次分明",
                "layout_pattern": "非对称网格布局，交错排列",
                "animation_types": ["scroll_triggered", "parallax"],
                "animation_details": "使用 GSAP ScrollTrigger 实现滚动触发动画",
                "tech_stack": ["gsap", "locomotive_scroll"],
                "interactive_features": ["smooth scroll", "hover effects"],
                "key_inspirations": ["大胆的排版", "深色模式"],
                "reusable_patterns": ["滚动触发渐显", "错开时序动画"],
                "implementation_tips": ["使用 Intersection Observer", "优化性能"],
                "overall_score": 8
            }
        }


def get_extraction_prompt(markdown_content: str, site_url: str) -> str:
    """生成结构化提取提示词"""
    return f"""你是一个专业的前端设计师和创意总监。
请分析以下网页内容，并严格按照 JSON Schema 输出分析结果。

## 网页内容（Markdown 格式）
{markdown_content}

## 输出要求
1. 必须输出有效的 JSON 格式
2. 必须包含所有必需字段
3. 颜色使用 HEX 格式
4. 枚举值使用小写下划线格式
5. 评分范围 1-10

请输出完整的 JSON 分析结果："""


def get_self_healing_prompt(error_message: str, markdown_content: str, site_url: str) -> str:
    """生成自愈修复提示词"""
    return f"""之前的提取失败了，错误信息：
{error_message}

请重新分析以下网页内容，并严格按照 JSON Schema 输出分析结果。

## 网页内容（Markdown 格式）
{markdown_content}

## 输出要求
1. 必须输出有效的 JSON 格式
2. 必须包含所有必需字段
3. 颜色使用 HEX 格式
4. 枚举值使用小写下划线格式
5. 评分范围 1-10

请输出完整的 JSON 分析结果："""


if __name__ == "__main__":
    schema = InspirationSchema.model_json_schema()
    print("InspirationSchema JSON Schema:")
    print(schema)