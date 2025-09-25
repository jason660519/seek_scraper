"""Persistence utilities for storing scraped job data."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

import pandas as pd

from src.config.config import config_manager
from src.models.models import Job


class DataService:
	"""Handle persistence of scraped job information to disk."""

	def __init__(self) -> None:
		self.storage = config_manager.storage_config

	def save_jobs_to_json(self, jobs: Iterable[Job], filename: str | None = None) -> Path:
		"""Persist job records to a JSON file and return the path."""

		data = [job.model_dump(mode="json") for job in jobs]
		if not filename:
			filename = self._generate_filename("json")

		path = self.storage.processed_dir / filename
		path.parent.mkdir(parents=True, exist_ok=True)

		with path.open("w", encoding="utf-8") as fh:
			json.dump(data, fh, ensure_ascii=False, indent=2)

		return path

	def save_jobs_to_csv(self, jobs: Iterable[Job], filename: str | None = None) -> Path:
		"""Persist job records to a CSV file and return the path."""

		if not filename:
			filename = self._generate_filename("csv")

		path = self.storage.processed_dir / filename
		path.parent.mkdir(parents=True, exist_ok=True)

		records = [job.model_dump(mode="python") for job in jobs]
		frame = pd.DataFrame(records)
		frame.to_csv(path, index=False, encoding="utf-8")
		return path

	def _generate_filename(self, extension: str) -> str:
		timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
		return f"seek_jobs_processed_{timestamp}.{extension}"


__all__ = ["DataService"]
