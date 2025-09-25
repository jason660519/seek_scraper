"""Base classes and shared utilities for scraper implementations."""

from __future__ import annotations

import asyncio
import time
from abc import ABC
from typing import Any, Dict, Optional

import httpx
from tenacity import AsyncRetrying, RetryCallState, retry_if_exception_type, stop_after_attempt, wait_random_exponential

from src.config.config import ConfigManager, config_manager
from src.utils.error_handler import ErrorHandler
from src.utils.logger import get_logger


class BaseScraper(ABC):
	"""Reusable foundation for SEEK scraper components."""

	def __init__(
		self,
		*,
		config: ConfigManager | None = None,
		client: Optional[httpx.AsyncClient] = None,
		logger_name: str = "scraper",
	) -> None:
		self.config = config or config_manager
		self.http_config = self.config.http_config
		self.logger = get_logger(logger_name)
		self.error_handler = ErrorHandler(logger_name)

		if client is None:
			self.client = httpx.AsyncClient(
				base_url=str(self.http_config.base_url),
				headers=self.config.build_headers(),
				timeout=self.http_config.timeout_seconds,
				follow_redirects=True,
			)
			self._owns_client = True
		else:
			self.client = client
			self._owns_client = False

		self._request_semaphore = asyncio.Semaphore(self.http_config.max_concurrency)
		self._throttle_lock = asyncio.Lock()
		self._last_request_monotonic = 0.0

	async def __aenter__(self) -> "BaseScraper":
		return self

	async def __aexit__(self, exc_type, exc, tb) -> None:
		await self.close()

	async def close(self) -> None:
		"""Close the underlying HTTP client if we own it."""

		if self._owns_client:
			await self.client.aclose()

	async def _throttle(self) -> None:
		"""Respect the configured minimum interval between outbound requests."""

		async with self._throttle_lock:
			now = time.monotonic()
			elapsed = now - self._last_request_monotonic
			interval = self.http_config.min_request_interval
			if elapsed < interval:
				await asyncio.sleep(interval - elapsed)
			self._last_request_monotonic = time.monotonic()

	async def request(
		self,
		method: str,
		url: str,
		*,
		params: Optional[Dict[str, Any]] = None,
		json: Optional[Dict[str, Any]] = None,
		headers: Optional[Dict[str, str]] = None,
		timeout: Optional[float] = None,
	) -> httpx.Response:
		"""Perform an HTTP request with throttling and retry behaviour."""

		async with self._request_semaphore:
			await self._throttle()

			retrying = AsyncRetrying(
				stop=stop_after_attempt(self.http_config.max_retries),
				wait=wait_random_exponential(
					multiplier=self.http_config.retry_backoff_min,
					max=self.http_config.retry_backoff_max,
				),
				reraise=True,
				retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
				before_sleep=self._before_retry,
			)

			async for attempt in retrying:
				with attempt:
					response = await self.client.request(
						method,
						url,
						params=params,
						json=json,
						headers=self._build_headers(headers),
						timeout=timeout or self.http_config.timeout_seconds,
					)
					response.raise_for_status()
					return response

	async def _before_retry(self, retry_state: RetryCallState) -> None:
		"""Log information before retrying and delegate to error handler."""

		error = retry_state.outcome.exception()  # type: ignore[assignment]
		if error is None:
			return

		context = {
			"message": "Request retry",
			"attempt": retry_state.attempt_number,
			"retry_state": retry_state,
		}
		await self.error_handler.handle(error, context)

	def _build_headers(self, extra: Optional[Dict[str, str]]) -> Dict[str, str]:
		headers = self.config.build_headers()
		if extra:
			headers.update(extra)
		return headers


__all__ = ["BaseScraper"]
