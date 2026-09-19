from __future__ import annotations

from pipesay.core.pipeline import Pipeline
from pipesay.core.registry import register

OUTPUTER_REGISTRY: dict = {}


def outputer(name: str | None = None):
    return register(OUTPUTER_REGISTRY, name)


class Outputer(Pipeline):
    registry = OUTPUTER_REGISTRY
    section = 'outputs'
    label = 'Outputer'

    def fire(self, sentences: list) -> None:
        self.run(sentences)

    @staticmethod
    def list_outputers():
        Outputer.list_all()