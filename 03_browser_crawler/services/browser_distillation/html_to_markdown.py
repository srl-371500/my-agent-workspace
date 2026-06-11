"""
HTML 到 Markdown 转换器
将网页 HTML 转换为纯文本 Markdown，剥离无用噪声
"""

import re
from typing import Optional
from bs4 import BeautifulSoup


def html_to_markdown(html_content: str, base_url: Optional[str] = None) -> str:
    """
    将 HTML 转换为 Markdown 格式
    
    Args:
        html_content: HTML 内容
        base_url: 基础 URL，用于解析相对链接
    
    Returns:
        Markdown 格式的文本
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 移除无用标签
    for tag in soup.find_all(['script', 'style', 'noscript', 'iframe', 'svg', 'canvas']):
        tag.decompose()
    
    # 移除注释
    for comment in soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in text):
        comment.extract()
    
    markdown_parts = []
    
    # 处理标题
    for i in range(1, 7):
        for heading in soup.find_all(f'h{i}'):
            text = heading.get_text(strip=True)
            if text:
                markdown_parts.append(f"{'#' * i} {text}\n")
    
    # 处理段落
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if text:
            markdown_parts.append(f"{text}\n")
    
    # 处理链接
    for a in soup.find_all('a'):
        href = a.get('href', '')
        text = a.get_text(strip=True)
        if href and text:
            if href.startswith('/') and base_url:
                href = f"{base_url.rstrip('/')}{href}"
            markdown_parts.append(f"[{text}]({href})\n")
    
    # 处理图片
    for img in soup.find_all('img'):
        alt = img.get('alt', '')
        src = img.get('src', '')
        if src:
            if src.startswith('/') and base_url:
                src = f"{base_url.rstrip('/')}{src}"
            markdown_parts.append(f"![{alt}]({src})\n")
    
    # 处理列表
    for ul in soup.find_all('ul'):
        for li in ul.find_all('li', recursive=False):
            text = li.get_text(strip=True)
            if text:
                markdown_parts.append(f"- {text}\n")
    
    for ol in soup.find_all('ol'):
        for i, li in enumerate(ol.find_all('li', recursive=False), 1):
            text = li.get_text(strip=True)
            if text:
                markdown_parts.append(f"{i}. {text}\n")
    
    # 处理代码块
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        if code:
            text = code.get_text(strip=True)
            lang = code.get('class', [''])[0].replace('language-', '') if code.get('class') else ''
            markdown_parts.append(f"```{lang}\n{text}\n```\n")
        else:
            text = pre.get_text(strip=True)
            if text:
                markdown_parts.append(f"```\n{text}\n```\n")
    
    # 处理引用
    for blockquote in soup.find_all('blockquote'):
        text = blockquote.get_text(strip=True)
        if text:
            lines = text.split('\n')
            for line in lines:
                markdown_parts.append(f"> {line}\n")
    
    # 处理表格
    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if cells:
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                markdown_parts.append("| " + " | ".join(cell_texts) + " |\n")
                if row == rows[0]:
                    markdown_parts.append("| " + " | ".join(["---"] * len(cells)) + " |\n")
    
    # 提取所有文本内容（作为补充）
    all_text = soup.get_text(separator='\n', strip=True)
    
    # 合并结果
    result = '\n'.join(markdown_parts)
    
    # 如果结果太少，使用全部文本
    if len(result) < 100:
        result = all_text
    
    # 清理多余空行
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    return result.strip()


def extract_meta_info(html_content: str) -> dict:
    """
    提取网页元信息
    
    Args:
        html_content: HTML 内容
    
    Returns:
        元信息字典
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    meta_info = {
        'title': '',
        'description': '',
        'keywords': '',
        'og_title': '',
        'og_description': '',
        'og_image': '',
    }
    
    # 提取 title
    title_tag = soup.find('title')
    if title_tag:
        meta_info['title'] = title_tag.get_text(strip=True)
    
    # 提取 meta 标签
    for meta in soup.find_all('meta'):
        name = meta.get('name', '').lower()
        property = meta.get('property', '').lower()
        content = meta.get('content', '')
        
        if name == 'description':
            meta_info['description'] = content
        elif name == 'keywords':
            meta_info['keywords'] = content
        elif property == 'og:title':
            meta_info['og_title'] = content
        elif property == 'og:description':
            meta_info['og_description'] = content
        elif property == 'og:image':
            meta_info['og_image'] = content
    
    return meta_info


if __name__ == "__main__":
    # 测试用例
    test_html = """
    <html>
    <head><title>Test Page</title></head>
    <body>
        <h1>Welcome</h1>
        <p>This is a test paragraph.</p>
        <ul>
            <li>Item 1</li>
            <li>Item 2</li>
        </ul>
        <a href="/about">About</a>
    </body>
    </html>
    """
    
    markdown = html_to_markdown(test_html, "https://example.com")
    print("Markdown output:")
    print(markdown)