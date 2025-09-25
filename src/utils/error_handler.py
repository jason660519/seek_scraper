"""Centralised error handling utilities for scraper components."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import httpx

from src.utils.logger import get_logger


class ErrorHandler:
	"""Application-wide error handler for HTTP and parsing operations."""

	def __init__(self, logger_name: str = "error") -> None:
		self.logger = get_logger(logger_name)

	async def handle(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
		"""Handle an exception raised by the crawler.

		Parameters
		----------
		error:
			The exception instance that was raised.
		context:
			Optional metadata describing the operation when the error occurred.
		"""

		context = context or {}

		if isinstance(error, httpx.HTTPStatusError):
			await self._handle_http_status_error(error, context)
		elif isinstance(error, httpx.TimeoutException):
			await self._handle_timeout(error, context)
		elif isinstance(error, httpx.RequestError):
			await self._handle_request_error(error, context)
		else:
			await self._handle_generic_error(error, context)

	async def _handle_http_status_error(
		self, error: httpx.HTTPStatusError, context: Dict[str, Any]
	) -> None:
		status = error.response.status_code if error.response is not None else "?"
		message = context.get("message", "HTTP status error encountered")

		if status == 429:
			cooldown = float(context.get("cooldown", 60.0))
			self.logger.warning(
				"%s | Status %s | Applying cooldown %.1fs",
				message,
				status,
				cooldown,
				extra={"context": context},
			)
			await asyncio.sleep(cooldown)
		elif 500 <= status < 600:
			self.logger.warning(
				"%s | Server error %s",
				message,
				status,
				extra={"context": context},
			)
		else:
			self.logger.error(
				"%s | HTTP error %s",
				message,
				status,
				exc_info=True,
				extra={"context": context},
			)

	async def _handle_timeout(
		self, error: httpx.TimeoutException, context: Dict[str, Any]
	) -> None:
		self.logger.warning(
			"%s | Timeout after %.1fs",
			context.get("message", "Request timeout"),
			context.get("timeout", 0.0),
			extra={"context": context},
		)

	async def _handle_request_error(
		self, error: httpx.RequestError, context: Dict[str, Any]
	) -> None:
		self.logger.error(
			"%s | Network error: %s",
			context.get("message", "Network error"),
			error,
			exc_info=True,
			extra={"context": context},
		)

	async def _handle_generic_error(self, error: Exception, context: Dict[str, Any]) -> None:
		self.logger.exception(
			"%s | Unexpected error: %s",
			context.get("message", "Unexpected error"),
			error,
			extra={"context": context},
		)


__all__ = ["ErrorHandler"]
