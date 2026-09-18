# PipeSay

> 一个可插拔的「句子流水线」框架：抓取 → 加工 → 输出。

PipeSay 将句子处理抽象为一条可配置的流水线。每个环节都通过装饰器注册、通过 YAML 组合，你无需改动核心代码，就能拼装出自己的玩法。

## 设计理念

- **三段式流水线**：`Fetcher` → `Processor` → `Outputer`，职责清晰，互不耦合。
- **注册式插件系统**：`@processor('name')` / `@processor('name')` / `@outputer('name')` 一键注册，签名自动反射为可配置参数。
- **YAML 驱动**：处理器与输出器均以声明式配置组合，支持全局参数与步骤级参数合并。
- **面向扩展**：核心只提供约定与调度，具体能力全部来自插件。

## 安装
```bash
    pip install -r requirements.txt
```

## 快速开始
```
## 命令行
```text
    usage: pipesay [-h] [-p {}] [-c PIPELINE_CONFIG]
```
| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `-p, --parser-mode` | parser解析器模式 | `None` |
| `-c, --pipeline-config` | 流水线配置 | `None` |
## 配置

处理器配置：
```yaml
    pipeline:
      - processor: to_weak
      - processor: i18n
        params:
          lan: [en, ja]

    global: {}
```
输出器配置：
```yaml
    outputs:
      - outputer: term
        params:
          auto_clear: True

    global: {}
```
`params` 会与 `global` 中同名步骤的配置合并，步骤级优先。

## 扩展

新增处理器：
```python
    from pipesay.processor.base import processor

    @processor('shout')
    def shout(sentences: list, mark: str = '!', log=None):
        """给每句话加上强调符号"""
        return [s + mark for s in sentences]
```
新增输出器：
```python
    from pipesay.outputers.base import outputer

    @outputer('count')
    def count(sentences: list, log=None):
        """只统计句子数量"""
        log(f"共 {len(sentences)} 句")
```
注册后即可在 YAML 中直接引用。函数签名中的 `sentences` 与 `log` 会被自动跳过，其余参数反射为可配置项。

查看已注册的步骤：
```python
    from pipesay.processor.base import Processor
    from pipesay.outputers.base import Outputer

    Processor.list_all()
    Outputer.list_all()
```
## 项目结构
```text
    src/pipesay/
    ├── main.py                # 入口
    ├── constants/             # 常量
    ├── fetcher/               # 获取器
    ├── processor/             # 处理器与注册表
    ├── outputers/             # 输出器与注册表
    ├── core/                  # 流水线执行器与注册装饰器
    ├── parser/                # 命令行解析
    └── utils/                 # 通用工具
```
## 工作原理
```text
    Fetcher ──▶ Processor ──▶ Outputer
        ▲              ▲        ▲
        └ pipeline.yaml┘--------┘
```
1. `Fetcher` 读取`fetchers`段，从数据源获取数据。
2. `Processor` 读取 `pipeline` 段，按序加工并逐级传递。
3. `Outputer` 读取 `outputs` 段，将结果交给输出器展示。

## License

MIT