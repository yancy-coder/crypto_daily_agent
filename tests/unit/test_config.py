"""Tests for config module."""

import pytest
from pathlib import Path
from pydantic import ValidationError
from crypto_daily_agent.config import Settings, ScoringWeights, load_settings


def test_scoring_weights_defaults():
    """测试评分权重默认值."""
    weights = ScoringWeights()
    assert weights.binance == 1.2
    assert weights.bitcoin_keyword == 0.9
    assert weights.ethereum_keyword == 0.7
    assert weights.tier1_source == 0.5


def test_scoring_weights_custom():
    """测试自定义评分权重."""
    weights = ScoringWeights(binance=2.0, bitcoin_keyword=1.5)
    assert weights.binance == 2.0
    assert weights.bitcoin_keyword == 1.5
    assert weights.ethereum_keyword == 0.7  # 默认值


def test_settings_defaults(tmp_path: Path, monkeypatch):
    """测试设置默认值."""
    monkeypatch.chdir(tmp_path)
    
    settings = Settings(_env_file=None)
    assert settings.tz == "Asia/Shanghai"
    assert settings.max_news_items == 10
    assert settings.storage_backend == "json"
    assert settings.enable_email is True


def test_settings_validation_max_news_items(tmp_path: Path, monkeypatch):
    """测试 max_news_items 验证."""
    monkeypatch.chdir(tmp_path)
    
    # 超出范围应该报错
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, max_news_items=100)
    assert "max_news_items" in str(exc_info.value)


def test_settings_validation_timeout(tmp_path: Path, monkeypatch):
    """测试 timeout 验证."""
    monkeypatch.chdir(tmp_path)
    
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, request_timeout_seconds=2)
    assert "request_timeout_seconds" in str(exc_info.value)


def test_settings_path_creation(tmp_path: Path, monkeypatch):
    """测试路径自动创建."""
    monkeypatch.chdir(tmp_path)
    
    output = tmp_path / "custom_output"
    state = tmp_path / "custom_state"
    
    settings = Settings(
        _env_file=None,
        output_dir=output,
        state_dir=state,
    )
    
    assert settings.output_dir == output
    assert settings.state_dir == state
    assert output.exists()
    assert state.exists()


def test_settings_scoring_weights(tmp_path: Path, monkeypatch):
    """测试评分权重配置."""
    monkeypatch.chdir(tmp_path)
    
    custom_weights = ScoringWeights(binance=2.5)
    settings = Settings(
        _env_file=None,
        scoring_weights=custom_weights,
    )
    
    assert settings.scoring_weights.binance == 2.5


def test_load_settings_function(tmp_path: Path, monkeypatch):
    """测试 load_settings 兼容函数."""
    monkeypatch.chdir(tmp_path)
    
    settings = load_settings()
    assert isinstance(settings, Settings)
    assert settings.tz == "Asia/Shanghai"


def test_settings_storage_backend_validation(tmp_path: Path, monkeypatch):
    """测试 storage_backend 验证."""
    monkeypatch.chdir(tmp_path)
    
    # 有效值
    settings = Settings(_env_file=None, storage_backend="json")
    assert settings.storage_backend == "json"
    
    settings = Settings(_env_file=None, storage_backend="sqlite")
    assert settings.storage_backend == "sqlite"


def test_settings_cleanup_days_validation(tmp_path: Path, monkeypatch):
    """测试 cleanup_days 验证."""
    monkeypatch.chdir(tmp_path)
    
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, storage_cleanup_days=0)
    assert "storage_cleanup_days" in str(exc_info.value)
    
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, storage_cleanup_days=31)
    assert "storage_cleanup_days" in str(exc_info.value)
