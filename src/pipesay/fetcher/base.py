import asyncio
import inspect

import yaml

from pipesay.core.registry import register

FETCHER_REGISTRY: dict = {}


def fetcher(name: str | None = None):
    return register(FETCHER_REGISTRY, name)


class Fetcher:
    registry = FETCHER_REGISTRY
    label = 'Fetcher'
    section = 'fetchers'

    def __init__(self, config_path=None, config_dict=None):
        if config_dict:
            self.config = config_dict
            self.config_source = "<config_dict>"
        elif config_path:
            self.config_source = config_path
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        else:
            raise ValueError("必须提供 config_path 或 config_dict")

        if self.section not in self.config:
            available = [k for k in self.config if k != 'global']
            raise ValueError(
                f"配置文件里找不到 {self.label} 需要的配置项 '{self.section}'。\n"
                f"  配置文件: {self.config_source}\n"
                f"  顶层已有的配置项: {available or '（空）'}\n"
                f"  请确认配置项名称是否拼写正确。"
            )

        raw = self.config[self.section] or {}

        # 兼容两种写法：dict 形式 {"name": ..., "params": {...}}
        #               或 list 形式 [{"name": ...}, ...]（但 fetcher 只有一步，取第一个）
        if isinstance(raw, list):
            if len(raw) != 1:
                raise ValueError(
                    f"Fetcher 只允许配置 1 个步骤，当前配置了 {len(raw)} 个"
                )
            raw = raw[0]

        self.name = raw.get('name')
        self.params = raw.get('params', {})
        self.global_config = self.config.get('global', {})

        if not self.name:
            raise ValueError(
                f"{self.section} 配置里缺少 name 字段。\n"
                f"  应为 {{'name': 'hitokoto', 'params': {{...}}}}"
            )
        if self.name not in self.registry:
            raise ValueError(
                f"未知 fetcher: {self.name}，已注册: {list(self.registry.keys())}"
            )

    def fetch(self) -> list:
        self.log(f'⏳ 执行 fetcher: {self.name}')
        func = self.registry[self.name]['func']
        final_params = {**self.global_config.get(self.name, {}), **self.params}
        try:
            result = self._call(func, final_params)
            self.log(f'✅ {self.name} 完成')
            return result
        except Exception as e:
            self.log(f'❌ {self.name} 失败: {e}')
            raise

    def _call(self, func, params):
        """注入 log，处理 async，不传 items（Fetcher 没有上游）"""
        params = {**params, 'log': self.log}
        result = func(**params)
        if inspect.iscoroutine(result):
            result = asyncio.run(result)
        return result

    def log(self, message: str):
        print(message)

    @classmethod
    def list_fetchers(cls):
        print("\n" + "=" * 60)
        print(f"已注册的 {cls.label}:")
        print("=" * 60)
        for name, info in cls.registry.items():
            print(f"\n【{name}】")
            if info['doc']:
                print(f"  说明: {info['doc']}")
            if info['params']:
                print("  参数:")
                for pname, pinfo in info['params'].items():
                    required = "必填" if pinfo['required'] else "可选"
                    default = (
                        f"，默认: {pinfo['default']}"
                        if pinfo['default'] is not None else ""
                    )
                    print(f"    - {pname}: {pinfo['type']} ({required}{default})")
            else:
                print("  无参数")
        print("=" * 60)