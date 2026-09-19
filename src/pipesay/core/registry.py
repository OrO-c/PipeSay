from __future__ import annotations

import inspect
from collections.abc import Callable


def register(registry: dict, name: str | None = None):
    """
    通用注册装饰器。
    用法：
        @register(PROCESSOR_REGISTRY, 'reverse')
        def reverse(sentences, log=None): ...
    """
    def decorator(func: Callable):
        key = name or func.__name__
        registry[key] = {
            'func': func,
            'params': extract_params(func),
            'doc': func.__doc__ or '',
        }
        return func          # 不套 wrapper，注册就是注册
    return decorator


def extract_params(func: Callable) -> dict:
    """从函数签名反射出可配置参数，跳过 self / sentences / log"""
    sig = inspect.signature(func)
    params = {}
    for pname, param in sig.parameters.items():
        if pname in ('self', 'sentences', 'log'):
            continue
        if param.default is inspect.Parameter.empty:
            params[pname] = {'type': 'any', 'default': None, 'required': True}
        else:
            params[pname] = {
                'type': type(param.default).__name__,
                'default': param.default,
                'required': False,
            }
    return params