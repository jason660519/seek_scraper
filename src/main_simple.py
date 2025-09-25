"""Simplified entry point for programmatic invocation."""

from __future__ import annotations

import asyncio
from argparse import Namespace

from src.main import build_argument_parser, run_crawler


def main() -> None:
	parser = build_argument_parser()
	args = parser.parse_args()
	asyncio.run(run_crawler(args))


def main_with_args(**kwargs) -> None:
	args = Namespace(**kwargs)
	asyncio.run(run_crawler(args))


if __name__ == "__main__":
	main()
