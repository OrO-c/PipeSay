import random
import time

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from pipesay.constants.constants import YIYAN_CATEGORY
from pipesay.fetcher.base import fetcher


@fetcher('hitokoto')
def hitokoto(generations: int, category: list, log=None):
    """从 Hitokoto 一言服务获取句子"""
    sentences = []
    last_sentence = ""
    retry_word = ""

    while len(sentences) < generations:
        log(f"{retry_word}正在向Hitokoto一言获取{len(sentences) + 1}/{generations}个句子...")
        fetch_sentence, author, from_work = _fetch_hitokoto(category)
        log(" ✅")

        if len(sentences) == 0 or fetch_sentence != last_sentence:
            if author is not None:
                sen_from = f"————{author}  《{from_work}》"
            else:
                sen_from = f"————《{from_work}》"
            width = len(fetch_sentence) + 4
            sentences.append(f"“{fetch_sentence}”\n{sen_from:>{width}}")
            last_sentence = fetch_sentence
            retry_word = ""
        elif last_sentence == fetch_sentence:
            log("由于api方缓存问题，此句和上句重复，本程序将睡2秒再重新获取😋")
            retry_word = "🔄 重试："
            time.sleep(2)

    return sentences


@fetcher('local')
def local(file_path: str, generations: int, log=None):
    """从本地文件随机挑选句子"""
    sentences = []
    with open(file=file_path, mode="r", encoding="utf-8") as f:
        local_sentence = f.readlines()
        for _ in range(generations):
            sentences.append(random.choice(local_sentence))
    return sentences


# ---- 私有辅助函数，不需要注册 ----
def _category_to_dict(category: list) -> dict:
    choose = []
    for c in category:
        for code, name in YIYAN_CATEGORY.items():
            if c == name:
                choose.append(code)
                break
    return {"c": choose} if choose else {}


def _fetch_hitokoto(category: list):
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    try:
        r = session.get(
            'https://v1.hitokoto.cn',
            timeout=(3.5, 6.5),
            params=_category_to_dict(category),
        )
    except requests.exceptions.Timeout:
        print("请求超时，请您检查网络和Hitokoto服务状态，并稍后再试")
        raise

    return r.json()["hitokoto"], r.json()["from_who"], r.json()["from"]