import asyncio
import inspect


class Pipeline:
    """
    通用管道执行器。
    子类只需要提供：
        - registry：注册表字典
        - section：配置里的键名（'pipeline' / 'outputs'）
        - label：日志里显示的名字（'Processor' / 'Outputer'）
    """
    registry: dict = {}
    section: str = ''
    label: str = 'Pipeline'

    def __init__(self, config_dict=None):
        if config_dict:
            self.config = config_dict
        else:
            raise ValueError("必须提供字典配置文件！")

        if self.section not in self.config:
            available = [k for k in self.config if k != 'global']
            raise ValueError(
                f"配置文件里找不到 {self.label} 需要的配置项 '{self.section}'。\n"
                f"  顶层已有的配置项: {available or '（空）'}\n"
                f"  请确认配置项名称是否拼写正确。"
            )
        # 注意：`processes: []` 或 `processes:`（值为 null）是合法配置，
        # 表示该环节有意留空、不执行任何步骤，此处静默转为空列表通过，
        # 不视为错误。只有 key 完全缺失才算配置错误（见上方检查）。 
        self.steps = self.config[self.section] or []
        self.global_config = self.config.get('global', {})

    def run(self, items: list) -> list:
        current = items
        total = len(self.steps)
        for idx, step in enumerate(self.steps, 1):
            name = step.get('name') or step.get('processor') or step.get('outputer')
            params = step.get('params', {})

            if name not in self.registry:
                raise ValueError(
                    f"未知步骤: {name}，已注册: {list(self.registry.keys())}"
                )

            self.log(f'⏳ [{idx}/{total}] 执行 {name}')
            func = self.registry[name]['func']
            final_params = {**self.global_config.get(name, {}), **params}

            try:
                result = self._call(func, current, final_params)
                current = result
                self.log(f'✅ {name} 完成')
            except Exception as e:
                self.log(f'❌ {name} 失败: {e}')
                raise

        self.log(f'{self.label} 全部处理完成！')
        return current

    def _call(self, func, items, params):
        """统一注入 log，统一处理 async"""
        params = {**params, 'log': self.log}
        result = func(items, **params)
        if inspect.iscoroutine(result):
            result = asyncio.run(result)
        return result

    def log(self, message: str):
        print(message)

    @classmethod
    def list_all(cls):
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