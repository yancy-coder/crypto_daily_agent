"""命令行接口."""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from crypto_daily_agent.config import Settings, load_settings
from crypto_daily_agent.application.digest_service import DigestService


def setup_logging(output_dir: Path) -> None:
    """配置日志."""
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "agent.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )


async def cmd_once(settings: Settings) -> None:
    """执行一次资讯汇总."""
    setup_logging(settings.output_dir)
    
    service = DigestService(settings)
    context = await service.run()
    
    # Render image
    from crypto_daily_agent.infrastructure.render.renderer import ImageRenderer
    renderer = ImageRenderer(settings.output_dir)
    image_path = renderer.render(context)
    
    print(f"Digest generated: {image_path}")
    
    # Send email if enabled
    if settings.enable_email:
        from crypto_daily_agent.infrastructure.sender import EmailSender
        sender = EmailSender(settings)
        await sender.send_digest(image_path, context)


def cmd_config_test(settings: Settings) -> None:
    """测试配置."""
    print("Configuration Test")
    print("=" * 40)
    print(f"TZ: {settings.tz}")
    print(f"Daily Push Time: {settings.daily_push_time}")
    print(f"Max News Items: {settings.max_news_items}")
    print(f"Storage Backend: {settings.storage_backend}")
    print(f"Email Enabled: {settings.enable_email}")
    print(f"Output Dir: {settings.output_dir}")
    print(f"State Dir: {settings.state_dir}")
    print("=" * 40)
    print("[OK] Configuration loaded successfully")


def main() -> None:
    """主入口."""
    parser = argparse.ArgumentParser(
        prog="crypto_daily_agent",
        description="每日加密资讯图片推送 Agent",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 2.0.0")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    subparsers.add_parser("once", help="执行一次资讯汇总")
    subparsers.add_parser("loop", help="启动定时调度 (未实现)")
    subparsers.add_parser("config-test", help="测试配置")
    
    args = parser.parse_args()
    settings = load_settings()
    
    if args.command == "once":
        asyncio.run(cmd_once(settings))
    elif args.command == "config-test":
        cmd_config_test(settings)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
