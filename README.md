# Crypto Daily Agent v2.0

每日加密资讯图片推送 Agent（重构版）

## 新特性 v2.0

- ✅ 插件化采集器架构
- ✅ Pydantic 配置验证
- ✅ 自动状态清理（解决无限增长问题）
- ✅ CoinMarketCap 价格数据
- ✅ 可配置评分权重
- ✅ 完整测试覆盖
- ✅ systemd timer 时区修复

## 安装

```bash
pip install -e ".[dev]"
playwright install chromium
```

## 使用

```bash
# 测试配置
python -m crypto_daily_agent config-test

# 执行一次
python -m crypto_daily_agent once

# 旧命令仍兼容
python -m agent.main --once
```

## 配置

编辑 `.env` 文件，新增配置项：

```bash
# 新增：评分权重（可选）
SCORING_WEIGHTS_BINANCE=1.2
SCORING_WEIGHTS_BITCOIN_KEYWORD=0.9

# 新增：存储后端（json 或 sqlite）
STORAGE_BACKEND=json
STORAGE_CLEANUP_DAYS=7

# 新增：CoinMarketCap API Key
COINMARKETCAP_API_KEY=your_key_here
```

---

## 旧文档（Agent v1）

### 1) 安装

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
cp .env.example .env
```

### 2) 配置

编辑 `.env`：

- `SMTP_*` / `EMAIL_*`：邮件推送参数（必填）。
- `NEWSAPI_KEY` / `X_BEARER_TOKEN`：可选，留空时自动降级。
- `DAILY_PUSH_TIME=08:00`
- `TZ=Asia/Shanghai`
- `ENABLE_EMAIL=true`（调试可设为 false）

### 3) 手动执行

```bash
python -m agent.main --once
```

输出图片在 `agent/output/`，日志在 `agent/output/agent.log`。

### 4) 常驻调度

```bash
python -m agent.main --loop
```

### 5) Linux cron 部署示例

```cron
CRON_TZ=Asia/Shanghai
0 8 * * * cd /opt/crypto_daily_agent && /opt/crypto_daily_agent/.venv/bin/python -m agent.main --once >> /opt/crypto_daily_agent/agent/output/cron.log 2>&1
```

### 6) systemd 示例（推荐）

参见 `deploy/crypto-daily.service` 与 `deploy/crypto-daily.timer`。
