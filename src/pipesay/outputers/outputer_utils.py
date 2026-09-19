import asyncio

from desktop_notifier import DesktopNotifier, Urgency

from pipesay.outputers.base import outputer
from pipesay.utils.utils import clear_screen, enter_to_next


@outputer('term')
def normal_terminal(sentences: list, auto_clear: bool=True, log=None):
    for index, text in enumerate(sentences):
        print(text)
        if index + 1 != len(sentences):
            print("=" * 30)
            enter_to_next("按回车来看下一句吧！")
            print("\n\n")
            if auto_clear:
                clear_screen()


@outputer('file')
def to_file(sentences: list, file_path: str, log=None):
    lines = [item + '\n\n' for item in sentences]
    with open(file=file_path, mode='a', encoding='utf-8') as f:
        f.writelines(lines)

@outputer('notify')
async def notify(sentences: list, level: str='normal', log=None):
    URGENCY_MAP = {
        "low": Urgency.Low,
        "normal": Urgency.Normal,
        "critical": Urgency.Critical,
    }

    urgency = URGENCY_MAP[level]

    notifier = DesktopNotifier(app_name="批量通知演示")

    for message in sentences:
        await notifier.send(
            title="PipeSay",
            message=message,
            urgency=urgency,
            sound=True,
        )

    await asyncio.sleep(3)

    log(f"已发送 {len(sentences)} 条通知，类型：{level}")

@outputer('tts')
def edge_tts_outputer(sentences: list[str], voice: str = "zh-CN-XiaoxiaoNeural", rate: str = "+0%", log=None) -> None:
    """使用 edge-tts 将句子批量合成为语音，再逐个播放"""
    import asyncio
    import os
    import tempfile
    from functools import partial

    import edge_tts
    from playsound3 import playsound

    from pipesay.utils.utils import enter_to_next

    async def _synthesize(text: str, output_path: str) -> None:
        communicate = edge_tts.Communicate(text, voice, rate=rate)
        await communicate.save(output_path)

    audio_paths: list[str] = []
    total = len(sentences)

    for index, text in enumerate(sentences, 1):
        log(f"🔊 正在合成第 {index}/{total} 句语音:")
        log(text)
        tmp_path = os.path.join(tempfile.gettempdir(), f"pipesay_tts_{index}.mp3")
        asyncio.run(partial(_synthesize, text, tmp_path)())
        audio_paths.append(tmp_path)

    log(f"✅ 全部 {total} 句合成完成，开始播放")

    for index, audio_path in enumerate(audio_paths, 1):
        enter_to_next(f"按回车播放第 {index}/{total} 句 ↩️")
        playsound(audio_path)
        log(f"✅ 第 {index}/{total} 句播放完成")

    for audio_path in audio_paths:
        try:
            os.remove(audio_path)
        except OSError:
            pass