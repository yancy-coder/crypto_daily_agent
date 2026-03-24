"""图片渲染器."""

from pathlib import Path
from datetime import datetime
from jinja2 import Template

from crypto_daily_agent.models import DigestContext


class ImageRenderer:
    """HTML 转 PNG 渲染器."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def render(self, context: DigestContext) -> Path:
        template_path = Path(__file__).parent / "template.html"
        html = Template(template_path.read_text(encoding="utf-8")).render(
            date_str=context.date_str,
            market_temperature=context.market_temperature,
            headline=context.headline,
            cards=context.cards,
        )
        
        ts = datetime.now().strftime("%Y%m%d")
        output_path = self.output_dir / f"crypto_digest_{ts}.png"
        temp_html = output_path.with_suffix(".html")
        temp_html.write_text(html, encoding="utf-8")
        
        try:
            self._render_with_playwright(temp_html, output_path)
        except Exception:
            self._render_with_pil(context, output_path)
        return output_path
    
    def _render_with_playwright(self, html_path: Path, output_path: Path) -> None:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": 1080, "height": 1520})
            page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
            page.screenshot(path=str(output_path), full_page=True)
            browser.close()
    
    def _render_with_pil(self, context: DigestContext, output_path: Path) -> None:
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (1080, 1520), color=(28, 34, 40))
        draw = ImageDraw.Draw(img)
        draw.text((48, 56), str(context.date_str), fill=(190, 198, 207))
        draw.text((48, 100), str(context.headline)[:80], fill=(214, 221, 227))
        y = 170
        for card in context.cards[:8]:
            draw.text((48, y), f"#{card['rank']} {card['title'][:60]}", fill=(159, 178, 196))
            y += 48
        img.save(output_path, format="PNG")
