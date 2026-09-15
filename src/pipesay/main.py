from pipesay.fetcher.fetcher import Fetcher
from pipesay.outputers import outputer_utils  # noqa: F401
from pipesay.outputers.base import Outputer
from pipesay.parser.parser import arg_process
from pipesay.processor import processor_utils  # noqa: F401
from pipesay.processor.base import Processor
from pipesay.utils.utils import clear_screen, enter_to_next


def main():
    args = arg_process()
    fetcher = Fetcher(args.get('fetcher_mode'), args.get('generations'), args.get('category'), args.get('file_path'),).new_fetcher()
    fetch_sentences = fetcher()
    processor = Processor(config_path=args.get('pipeline_config'))
    speak_sentences = processor.process(fetch_sentences)
    enter_to_next("已经处理完成，按回车开始输出")
    clear_screen()
    outputer = Outputer(config_path=args.get('pipeline_config'))
    outputer.fire(speak_sentences)

if __name__ == "__main__":
    main()