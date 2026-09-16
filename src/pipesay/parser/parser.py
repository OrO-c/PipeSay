import argparse


def _arg_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='PipeSay句子流水线')
    parser.add_argument('-p', '--pipeline-config', dest="pipeline_config", type=str, default=None, help='流水线配置')
    return parser.parse_args()


def arg_process():
    args = _arg_parser()
    return args.pipeline_config