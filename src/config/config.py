"""Configuration management for the SEEK job crawler project."""

from __future__ import annotations

import os
import random
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl

try:  # pragma: no cover - optional dependency might fail silently
	from fake_useragent import FakeUserAgent  # type: ignore
except Exception:  # pragma: no cover
	FakeUserAgent = None  # type: ignore


class AppConfig(BaseModel):
	"""General application-level configuration."""

	name: str = Field(default="seek-job-crawler", description="Application name")
	version: str = Field(default=os.getenv("APP_VERSION", "1.0.0"))
	environment: str = Field(default=os.getenv("APP_ENV", "development"))
	debug: bool = Field(default=os.getenv("APP_DEBUG", "false").lower() == "true")


class LoggingConfig(BaseModel):
	"""Logging configuration."""

	level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))
	format: str = Field(
		default=os.getenv(
			"LOG_FORMAT",
			"%(asctime)s | %(levelname)s | %(name)s | %(message)s",
		)
	)
	console_enabled: bool = Field(
		default=os.getenv("LOG_CONSOLE_ENABLED", "true").lower() == "true"
	)
	file_enabled: bool = Field(
		default=os.getenv("LOG_FILE_ENABLED", "true").lower() == "true"
	)
	max_file_size: int = Field(default=int(os.getenv("LOG_MAX_FILE_SIZE", 5 * 1024 * 1024)))
	backup_count: int = Field(default=int(os.getenv("LOG_BACKUP_COUNT", 5)))


class HttpConfig(BaseModel):
	"""HTTP client configuration."""

	base_url: HttpUrl = Field(
		default=os.getenv("SEEK_BASE_URL", "https://www.seek.com.au")
	)
	search_endpoint: str = Field(
		default=os.getenv("SEEK_SEARCH_ENDPOINT", "/api/chalice-search/v4/search")
	)
	job_detail_endpoint: str = Field(
		default=os.getenv("SEEK_JOB_DETAIL_ENDPOINT", "/job/{job_id}")
	)
	timeout_seconds: float = Field(default=float(os.getenv("HTTP_TIMEOUT", 20.0)))
	max_retries: int = Field(default=int(os.getenv("HTTP_MAX_RETRIES", 3)))
	retry_backoff_min: float = Field(
		default=float(os.getenv("HTTP_RETRY_BACKOFF_MIN", 1.0))
	)
	retry_backoff_max: float = Field(
		default=float(os.getenv("HTTP_RETRY_BACKOFF_MAX", 6.0))
	)
	min_request_interval: float = Field(
		default=float(os.getenv("HTTP_MIN_REQUEST_INTERVAL", 0.6))
	)
	max_concurrency: int = Field(
		default=int(os.getenv("HTTP_MAX_CONCURRENCY", 5))
	)
	fallback_user_agent: str = Field(
		default=os.getenv(
			"HTTP_FALLBACK_USER_AGENT",
			"Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
			" AppleWebKit/537.36 (KHTML, like Gecko)"
			" Chrome/118.0.0.0 Safari/537.36",
		)
	)
	default_headers: Dict[str, str] = Field(
		default_factory=lambda: {
			"Accept": "application/json,text/html;q=0.9",
			"Accept-Language": "en-AU,en;q=0.9",
			"Cache-Control": "no-cache",
			"Pragma": "no-cache",
		}
	)


class ProxyConfig(BaseModel):
	"""Proxy related configuration."""

	enabled: bool = Field(default=os.getenv("PROXY_ENABLED", "false").lower() == "true")
	provider_url: Optional[HttpUrl] = Field(
		default=os.getenv("PROXY_PROVIDER_URL") or None
	)
	auth_token: Optional[str] = Field(default=os.getenv("PROXY_PROVIDER_TOKEN"))
	rotation_seconds: int = Field(default=int(os.getenv("PROXY_ROTATION_SECONDS", 300)))
	static_proxies: List[str] = Field(
		default_factory=lambda: [
			proxy.strip()
			for proxy in os.getenv("PROXY_STATIC_LIST", "").split(",")
			if proxy.strip()
		]
	)


class StorageConfig(BaseModel):
	"""Filesystem storage locations."""

	root_dir: Path = Field(default=Path("data"))
	raw_dir: Path = Field(default=Path("data/raw"))
	processed_dir: Path = Field(default=Path("data/processed"))
	logs_dir: Path = Field(default=Path("data/logs"))

	def model_post_init(self, __context: Dict[str, object]) -> None:  # type: ignore[override]
		for path in (self.root_dir, self.raw_dir, self.processed_dir, self.logs_dir):
			Path(path).mkdir(parents=True, exist_ok=True)


class ConfigManager:
	"""Centralised access to configuration values."""

	def __init__(self) -> None:
		load_dotenv(override=False)

		self.app_config = AppConfig()
		self.logging_config = LoggingConfig()
		self.http_config = HttpConfig()
		self.proxy_config = ProxyConfig()
		self.storage_config = StorageConfig()

		self._user_agent_provider = self._build_user_agent_provider()

	def _build_user_agent_provider(self):
		if FakeUserAgent is None:
			return None

		cache_dir = Path(os.getenv("FAKE_USERAGENT_CACHE", "data/cache"))
		cache_dir.mkdir(parents=True, exist_ok=True)

		try:  # pragma: no cover - network dependent
			return FakeUserAgent(cache_path=str(cache_dir / "fake_useragent.json"))
		except Exception:
			return None

	def get_user_agent(self) -> str:
		"""Return a random user agent string."""

		if self._user_agent_provider is not None:  # pragma: no cover - randomness
			try:
				return self._user_agent_provider.random  # type: ignore[attr-defined]
			except Exception:
				pass

		fallback_pool = [
			self.http_config.fallback_user_agent,
			"Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0)"
			" AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
			"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
			" (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
		]
		return random.choice(fallback_pool)

	def build_headers(self, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
		"""Construct default headers for outbound requests."""

		headers = dict(self.http_config.default_headers)
		headers["User-Agent"] = self.get_user_agent()
		if extra:
			headers.update(extra)
		return headers


config_manager = ConfigManager()

__all__ = [
	"AppConfig",
	"LoggingConfig",
	"HttpConfig",
	"ProxyConfig",
	"StorageConfig",
	"ConfigManager",
	"config_manager",
]
