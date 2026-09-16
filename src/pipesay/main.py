from pipesay.fetcher import fetcher_utils  # noqa: F401
from pipesay.fetcher.base import Fetcher
from pipesay.outputers import outputer_utils  # noqa: F401
from pipesay.outputers.base import Outputer
from pipesay.parser.parser import arg_process
from pipesay.processor import processor_utils  # noqa: F401
from pipesay.processor.base import Processor
from pipesay.utils.utils import clear_screen, enter_to_next


def main():
    config = arg_process()
    fetcher = Fetcher(config)
    fetch_sentences = fetcher.fetch()
    processor = Processor(config)
    speak_sentences = processor.process(fetch_sentences)
    enter_to_next("已经处理完成，按回车开始输出")
    clear_screen()
    outputer = Outputer(config)
    outputer.fire(speak_sentences)

if __name__ == "__main__":
    main()