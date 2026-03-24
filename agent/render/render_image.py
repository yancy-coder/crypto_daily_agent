from __future__ import annotations

from pathlib import Path
from typing import Dict

from jinja2 import Template
from PIL import Image, ImageDraw


def _fallback_image(output_path: Path, context: Dict[str, object]) -> None:
    img = Image.new("RGB", (1080, 1520), color=(28, 34, 40))
    draw = ImageDraw.Draw(img)
    draw.text((48, 56), str(context.get("date_str", "")), fill=(190, 198, 207))
    draw.text((48, 100), str(context.get("headline", ""))[:80], fill=(214, 221, 227))
    y = 170
    for card in context.get("cards", [])[:8]:
        draw.text((48, y), f"#{card['rank']} {card['title'][:60]}", fill=(159, 178, 196))
        y += 48
    img.save(output_path, format="PNG")


def render_png(template_path: Path, output_path: Path, context: Dict[str, object]) -> Path:
    html = Template(template_path.read_text(encoding="utf-8")).render(**context)
    temp_html = output_path.with_suffix(".html")
    temp_html.write_text(html, encoding="utf-8")

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1080, "height": 1520})
            page.goto(temp_html.resolve().as_uri(), wait_until="networkidle")
            page.screenshot(path=str(output_path), full_page=True)
            browser.close()
    except Exception:
        _fallback_image(output_path, context)

    return output_path
