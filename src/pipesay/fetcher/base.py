from pipesay.core.pipeline import Pipeline
from pipesay.core.registry import register

FETCHER_REGISTRY: dict = {}


def fetcher(name: str | None = None):
    return register(FETCHER_REGISTRY, name)


class Fetcher(Pipeline):
    registry = FETCHER_REGISTRY
    section = 'fetchers'
    label = 'Fetcher'

    def __init__(self, config_path=None, config_dict=None):
        super().__init__(config_path=config_path, config_dict=config_dict)
        if len(self.steps) != 1:
            raise ValueError(
                f"Fetcher 只允许配置 1 个步骤，当前配置了 {len(self.steps)} 个"
            )

    def fetch(self) -> list:
        return self.run([])

    @staticmethod
    def list_fetchers():
        Fetcher.list_all()