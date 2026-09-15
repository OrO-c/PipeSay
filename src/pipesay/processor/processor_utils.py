from pipesay.processor.base import processor


@processor('reverse')
def reverse(sentences: list, log=None):
    """反转字符串"""
    rl = []
    for s in sentences:
        rl.append(s[::-1])
    return rl

@processor('to_weak')
def toweak(sentences: list, log=None):
    """让你的话变得虚弱无比"""
    import random

    import jieba
    
    PUNCT = set("，。！？；：、")
    return_list = []

    for s in sentences:
        parts = []
        current = ""
        for char in s:
            if char in PUNCT:
                if current:
                    parts.append(current)
                parts.append(char)
                current = ""
            else:
                current += char
        if current:
            parts.append(current)

        # 先找出所有可分词的片段索引
        word_part_indices = [i for i, p in enumerate(parts) if p not in PUNCT]

        # 整句只选一个片段来插入省略号
        if word_part_indices:
            chosen = random.choice(word_part_indices)
        else:
            chosen = None

        result = []
        for i, part in enumerate(parts):
            if part in PUNCT:
                result.append(part)
            else:
                words = jieba.lcut(part)
                if not words:
                    continue
                if i == chosen:
                    idx = random.randint(1, len(words) - 1) if len(words) > 1 else 0
                    words.insert(idx, "……")
                result.extend(words)

        return_list.append(''.join(result))

    return return_list

@processor('i18n')
def i18n(sentences, lan: list, log=None):
    """保持你原来的函数签名和封装结构"""
    import time
    import unicodedata
    from concurrent.futures import ThreadPoolExecutor

    import translators as ts
    
    def _translate_one(s, l):
        translated = ts.translate_text(s, translator='bing', to_language=l)
        fixed = unicodedata.normalize('NFKC', translated)
        time.sleep(0.5)
        log(f"{l}获取完成啦！为防止风控，i18n工具需要0.5秒再打请求")
        return fixed

    rl = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        for s in sentences:
            i18n_list = []
            futures = [executor.submit(_translate_one, s, l) for l in lan]
            for f in futures:
                i18n_list.append(f.result())
            result = ''.join(['\n\n' + item for item in i18n_list])
            rl.append(result)
    return rl


@processor('ads')
def ads(sentences, base_url: str, model: str, api_key: str, category: list | None = None, log=None):
    import json

    from openai import OpenAI
    
    if category is None:
        category = ['美食', '科技', '美妆', '旅行', '亲子']
    
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    system_prompt = """
        You are an AI assistant skilled at generating short ad copy in the style of Google Ads.
        The user will provide a list of categories (e.g., ['Food', 'Tech', 'Beauty']), and you need to randomly select one category from the list and generate an ad for it.

        Requirements:

        Style: Google Ads RSA style. The title should include a selling point + a call to action (CTA). The description should add trust signals or promotional offers.
        
        In a user's request, a number is usually attached as the number of ads to generate. You need to generate according to that number, and always return using a JSON list even though the user may only ask for one.

        Output: Strict JSON format with the following two fields:

        "title": no more than 30 characters, attention-grabbing

        "description": no more than 45 characters, including a call to action

        Product/brand names must be fictional but sound realistic and trustworthy.

        Language adaptation: Generate the ad in the primary language of the input category list (if mixed, prefer Chinese).

        Output only the JSON object – no extra text, comments, or Markdown formatting.

        Example 1 (Chinese):
        INPUT: ['美食', '科技', '美妆', '旅行', '亲子'],2
        OUTPUT: [{"title": "5999元起｜东京七日半自助游", "description": "正规旅行社，资深导游带队，无强制购物。立即询价！"}, {"title":"青春期孩子不听管教 | 育儿帮", "description": "点击连线专业咨询师"}]

        Example 2 (English):
        INPUT: ['Electronics', 'Fitness', 'Home'],1
        OUTPUT: [{"title": "50% Off｜SonicGlide Toothbrush", "description": "Advanced sonic cleaning. Free shipping, order now!"}]
    """

    user_prompt = f"{category},{len(sentences)}"

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )

    llm_result: list = json.loads(response.choices[0].message.content)
    
    ad_text: list = [f"\n\n[Ads]\n{r['title']}\n{r['description']}" for r in llm_result]
    result = [x + y for x, y in zip(sentences, ad_text)]
    
    return result

@processor('cowsay')
def cow(sentences: list, cow: str = "default", random_cow: bool = False, log=None):
    import random

    from cowsay import cowsay, list_cows
    rl = []
    
    if random_cow:
        cow = random.choice(list_cows())
    
    for sentence in sentences:
        lines = sentence.split("\n")
        max_line_len = max(len(line) for line in lines)
        dynamic_width = max_line_len + 4
        rl.append(cowsay(sentence, cow=cow, width=dynamic_width))
    
    return rl


@processor('ban')
def ban(sentences: list, ban_count: int=1, log=None):
    import random
    rl = []
    
    for s in sentences:
        cur_sen = s
        for a in range(ban_count):
            index = random.randint(0, len(cur_sen) - 1)
            cur_sen = cur_sen[:index] + "**" + cur_sen[index+1:]
        rl.append(cur_sen)
    
    return rl

@processor('rep2')
def replace_repeat(sentences: list, rep_sen: str, log=None):
    """
    将rep_sen中的内容循环重复替换sen内容
    
    Args:
        rep_sen(str): 准备好的来循环替换的句子
    
    Example:
        sentence为20个字符
        >>> print(replace_repeat("Goodbye"))
        GoodbyeGoodbyeGoodby
        注意，有一个e因为超出句子长度被截断了哦
    """
    rl = []
    
    for s in sentences:
        target_len = len(s)
        q, r = divmod(target_len, len(rep_sen))
        result = rep_sen * q + rep_sen[:r]
        rl.append(result)
    return rl

@processor('repeat')
def repeat(sentences: list, count: int=2, log=None):
    rl = []
    
    for s in sentences:
        rl.append(s * count)
    
    return rl