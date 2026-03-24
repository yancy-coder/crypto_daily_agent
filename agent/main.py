from __future__ import annotations

import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler

from agent.config import load_settings
from agent.deliver.email_sender import send_digest_email
from agent.pipeline.normalize import process
from agent.pipeline.summarize import build_render_context
from agent.render.render_image import render_png
from agent.sources.binance import BinanceAnnouncementCollector
from agent.sources.coindesk_rss import CoinDeskRssCollector
from agent.sources.newsapi import NewsApiCollector
from agent.sources.onchain_rss import OnchainRssCollector
from agent.sources.x_list import XListCollector

LOGGER = logging.getLogger("crypto_daily_agent")


def setup_logging(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "agent.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler()],
    )


def collect_all():
    settings = load_settings()
    collectors = [
        BinanceAnnouncementCollector(settings),
        CoinDeskRssCollector(),
        NewsApiCollector(settings),
        XListCollector(settings),
        OnchainRssCollector(),
    ]
    all_items = []
    for c in collectors:
        name = c.__class__.__name__
        try:
            data = c.fetch()
            LOGGER.info("collector=%s items=%s", name, len(data))
            all_items.extend(data)
        except Exception as exc:
            LOGGER.exception("collector_failed=%s error=%s", name, exc)
    return all_items


def run_once() -> None:
    settings = load_settings()
    setup_logging(settings.output_dir)
    LOGGER.info("digest_run_started")

    items = collect_all()
    selected = process(items, settings.max_news_items, settings.state_file)
    context = build_render_context(selected)

    ts = datetime.now(tz=ZoneInfo(settings.tz)).strftime("%Y%m%d")
    out = settings.output_dir / f"crypto_digest_{ts}.png"
    template_path = Path(__file__).resolve().parent / "render" / "template.html"
    render_png(template_path, out, context)

    subject = f"[Crypto Daily] {context['date_str']} 市场资讯"
    body = (
        f"今日为你筛选 {len(selected)} 条加密资讯。\n"
        f"市场温度：{context['market_temperature']}\n"
        "详见附件图片。"
    )
    if settings.enable_email:
        try:
            send_digest_email(settings, out, subject, body)
            LOGGER.info("email_sent file=%s", out)
        except Exception as exc:
            LOGGER.exception("email_send_failed error=%s", exc)
            # Fallback: try sending alert text-only mail.
            try:
                send_digest_email(
                    settings,
                    out,
                    "[Crypto Daily][ALERT] 推送失败",
                    f"本次推送失败: {exc}\n请检查日志与配置。",
                )
            except Exception:
                LOGGER.error("alert_email_failed")
                raise
    else:
        LOGGER.info("email_disabled file=%s", out)


def run_scheduler() -> None:
    settings = load_settings()
    setup_logging(settings.output_dir)
    scheduler = BlockingScheduler(timezone=settings.tz)
    hour, minute = settings.daily_push_time.split(":")
    scheduler.add_job(run_once, "cron", hour=int(hour), minute=int(minute), id="daily_digest")
    LOGGER.info("scheduler_started at=%s tz=%s", settings.daily_push_time, settings.tz)
    scheduler.start()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        run_once()
    elif len(sys.argv) > 1 and sys.argv[1] == "--loop":
        run_scheduler()
    else:
        print("Usage: python -m agent.main --once | --loop")
        time.sleep(0.2)
