# src/pipesay/__init__.py
from importlib.metadata import PackageNotFoundError, version

from pipesay.core.pipeline import Pipeline
from pipesay.core.registry import register
from pipesay.fetcher.base import Fetcher
from pipesay.outputers.base import Outputer
from pipesay.processor.base import Processor

try:
    __version__ = version("pipesay")
except PackageNotFoundError:
    __version__ = "0.0.0"
__all__ = ["Fetcher", "Outputer", "Pipeline", "Processor", "register"]