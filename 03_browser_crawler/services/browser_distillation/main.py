import asyncio
import yaml
from pathlib import Path
from browser_use import Browser
from browser_use.browser.context import BrowserContext
from langchain_openai import ChatOpenAI


def load_config():
    config_path = Path(__file__).parent.parent.parent / "config" / "settings.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


async def create_browser_context(config):
    browser_config = config.get("browser", {})
    browser = Browser(
        headless=browser_config.get("headless", True),
        browser_type=browser_config.get("type", "chromium"),
    )
    return browser


async def create_llm(config):
    api_config = config.get("api", {})
    return ChatOpenAI(
        model=api_config.get("model", "mimo-v2.5-pro"),
        base_url=api_config.get("endpoint", "https://api.example.com/v1"),
        api_key=api_config.get("api_key", "your_api_key_here"),
    )


async def browse_website(url, task_description):
    config = load_config()
    browser = await create_browser_context(config)
    llm = await create_llm(config)
    
    async with browser:
        context = BrowserContext(browser=browser)
        async with context:
            page = await context.get_current_page()
            await page.goto(url)
            
            content = await page.content()
            
            result = {
                "url": url,
                "title": await page.title(),
                "content_length": len(content),
                "task": task_description,
            }
            
            return result


async def main():
    url = "https://example.com"
    task = "Extract the main content and title from this page"
    
    result = await browse_website(url, task)
    print(f"Browsing result: {result}")


if __name__ == "__main__":
    asyncio.run(main())