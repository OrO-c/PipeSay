from __future__ import annotations

import argparse

import yaml

_registry = {}

from typing import Callable


def parser(name: str | None = None) -> Callable:
    """用于注册 parser 解析器的注册表装饰器。

    Args:
        name: 在 registry 字典中的键名。若为 None，则使用被装饰函数的
            函数名作为键名。

    Returns:
        一个装饰器函数，它接收目标函数并将其注册到 _registry 字典中，
        同时原样返回该函数（不改变其行为）。
    """
    def decorator(func: Callable) -> Callable:
        key = name or func.__name__
        _registry[key] = func
        return func
    return decorator

def _argv_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='PipeSay句子流水线')
    parser.add_argument('-p', '--parser-mode', dest='parser_mode', type=str, default=None, choices=_registry.keys(), help='parser解析器模式')
    parser.add_argument('-c', '--pipeline-config', dest="pipeline_config", type=str, default=None, help='流水线配置')
    return parser.parse_args()


def get_config() -> dict:
    args = _argv_parser()
    
    if args.parser_mode is not None and args.pipeline_config is not None:
        raise ValueError("parser_mode 和 pipeline_config 不能同时指定")

    if args.parser_mode is None and args.pipeline_config is None:
        raise ValueError("必须指定 parser_mode 或 pipeline_config 之一")

    if args.pipeline_config is not None:
        return local_yaml_to_dict(args.pipeline_config)

    if args.parser_mode not in _registry:
        raise ValueError(f"未知的 parser_mode: {args.parser_mode}")

    return _registry[args.parser_mode]()

def local_yaml_to_dict(yaml_path:str) -> dict:
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    return data