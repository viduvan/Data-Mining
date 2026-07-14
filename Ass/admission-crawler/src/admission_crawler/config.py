"""
config.py — Pydantic settings loading từ YAML/Env.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, BaseModel

class AppConfig(BaseModel):
    name: str = "admission-crawler"
    version: str = "0.1.0"
    parser_version: str = "v0.1.0"
    province_filter: str = "Hà Nội"
    years_default: List[int] = Field(default_factory=lambda: list(range(2016, 2026)))

class HttpConfig(BaseModel):
    concurrency: int = 1
    connect_timeout_seconds: int = 10
    read_timeout_seconds: int = 30
    total_timeout_seconds: int = 45
    user_agent: str = "UniversityCutoffResearchBot/1.0 (+contact: research@example.com; educational research)"
    accept: str = "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8"
    accept_language: str = "vi-VN,vi;q=0.9,en;q=0.8"
    follow_redirects: bool = True
    max_redirects: int = 5

class RateLimitConfig(BaseModel):
    min_delay_seconds: float = 5.0
    max_delay_seconds: float = 9.0
    requests_per_hour_cap: int = 300
    requests_per_day_cap: int = 1000

class RetryConfig(BaseModel):
    max_attempts: int = 3
    retry_statuses: List[int] = Field(default_factory=lambda: [408, 425, 500, 502, 503, 504])
    backoff_seconds: List[int] = Field(default_factory=lambda: [30, 90, 300])

class CircuitBreakerConfig(BaseModel):
    consecutive_failures: int = 5
    cooldown_minutes: int = 30

class RateLimit429Config(BaseModel):
    first_hit_sleep_minutes: int = 30
    second_hit_stop_run: bool = True
    third_hit_in_24h_lock_hours: int = 24

class CacheConfig(BaseModel):
    enabled: bool = True
    ttl_days: Dict[str, int] = Field(default_factory=lambda: {"2016-2023": 365, "2024": 180, "2025": 30})
    html_dir: str = "data/raw_html"
    compress: bool = True

class DatabaseConfig(BaseModel):
    url: str = "sqlite:///data/crawler.db"
    echo: bool = False

class QualityGateConfig(BaseModel):
    max_http_failure_rate: float = 0.02
    max_parse_failure_rate: float = 0.02
    max_empty_detail_rate: float = 0.05
    max_consecutive_schema_failures: int = 3

class TargetsConfig(BaseModel):
    base_url: str = "https://vietnamnet.vn"
    robots_url: str = "https://vietnamnet.vn/robots.txt"
    index_path_template: str = "/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-{year}"
    allowed_domain: str = "vietnamnet.vn"
    allowed_path_prefix: str = "/giao-duc/diem-thi/tra-cuu-diem-chuan-cd-dh-"

class LoggingConfig(BaseModel):
    level: str = "INFO"
    format: str = "json"
    file: str = "logs/crawler.log"

class Settings(BaseSettings):
    app: AppConfig = Field(default_factory=AppConfig)
    http: HttpConfig = Field(default_factory=HttpConfig)
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    retry: RetryConfig = Field(default_factory=RetryConfig)
    circuit_breaker: CircuitBreakerConfig = Field(default_factory=CircuitBreakerConfig)
    rate_limit_429: RateLimit429Config = Field(default_factory=RateLimit429Config)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    quality_gate: QualityGateConfig = Field(default_factory=QualityGateConfig)
    targets: TargetsConfig = Field(default_factory=TargetsConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    model_config = SettingsConfigDict(
        env_prefix="CRAWLER_",
        env_nested_delimiter="__",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

def deep_update(d: Dict[str, Any], u: Dict[str, Any]) -> Dict[str, Any]:
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            d[k] = deep_update(d[k], v)
        else:
            d[k] = v
    return d

def load_settings(env: str = "default") -> Settings:
    """Load settings from YAML files."""
    base_dir = Path(__file__).resolve().parent.parent.parent
    configs_dir = base_dir / "configs"
    
    # Load default.yaml
    default_config_path = configs_dir / "default.yaml"
    config_dict = {}
    if default_config_path.exists():
        with open(default_config_path, "r", encoding="utf-8") as f:
            config_dict = yaml.safe_load(f) or {}
            
    # Load env specific yaml (e.g., development.yaml)
    if env != "default":
        env_config_path = configs_dir / f"{env}.yaml"
        if env_config_path.exists():
            with open(env_config_path, "r", encoding="utf-8") as f:
                env_dict = yaml.safe_load(f) or {}
                config_dict = deep_update(config_dict, env_dict)
                
    return Settings(**config_dict)

settings = load_settings()
