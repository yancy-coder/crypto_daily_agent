# Crypto Daily Agent

每日加密资讯图片推送 Agent（云服务器部署），默认北京时间 08:00 推送邮件。

## 1) 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env
```

## 2) 配置

编辑 `.env`：

- `SMTP_*` / `EMAIL_*`：邮件推送参数（必填）。
- `NEWSAPI_KEY` / `X_BEARER_TOKEN`：可选，留空时自动降级。
- `DAILY_PUSH_TIME=08:00`
- `TZ=Asia/Shanghai`
- `ENABLE_EMAIL=true`（调试可设为 false）

## 3) 手动执行

```bash
python -m agent.main --once
```

输出图片在 `agent/output/`，日志在 `agent/output/agent.log`。

## 4) 常驻调度

```bash
python -m agent.main --loop
```

## 5) Linux cron 部署示例

```cron
CRON_TZ=Asia/Shanghai
0 8 * * * cd /opt/crypto_daily_agent && /opt/crypto_daily_agent/.venv/bin/python -m agent.main --once >> /opt/crypto_daily_agent/agent/output/cron.log 2>&1
```

## 6) systemd 示例（推荐）

参见 `deploy/crypto-daily.service` 与 `deploy/crypto-daily.timer`。
