import re

def merge_lrc(s: str, ts: str) -> str:
    """
    合并原歌词和翻译歌词为双语LRC格式。
    :param s: 原歌词LRC文本
    :param ts: 翻译歌词LRC文本
    :return: 合并后的LRC文本
    """
    # 如果其中一个为空，直接返回另一个
    if not s:
        return ts or ''
    if not ts:
        return s or ''

    time_pat = re.compile(r"\[(\d+):(\d+\.\d+)\](.*)")

    def parse_lrc(text):
        entries = []
        for line in text.splitlines():
            m = time_pat.match(line)
            if not m:
                continue
            mm, ss, lyric = m.groups()
            total_ms = int(mm) * 60000 + int(float(ss) * 1000)
            entries.append((total_ms, lyric.strip()))
        return entries

    orig = parse_lrc(s)
    trans = parse_lrc(ts)
    if not orig:
        return ts

    # 为每句原歌词匹配最接近的翻译（被占用后移除）
    trans_pool = trans[:]
    matched_trans = {}
    for i in reversed(range(len(orig))):  # 从后往前分配翻译
        o_time, _ = orig[i]
        if not trans_pool:
            break
        closest_idx = min(range(len(trans_pool)), key=lambda j: abs(trans_pool[j][0] - o_time))
        matched_trans[i] = trans_pool[closest_idx][1]
        trans_pool.pop(closest_idx)

    # 构造三元组：未匹配的翻译用原句代替
    merged = []
    for i, (o_time, o_text) in enumerate(orig):
        t_text = matched_trans.get(i, o_text)
        merged.append((o_time, o_text, t_text))

    # 排序
    merged.sort(key=lambda x: x[0])

    # 毫秒转LRC时间标签
    def fmt_ts(ms: int) -> str:
        mm = ms // 60000
        ss = (ms % 60000) // 1000
        mss = ms % 1000
        return f"[{mm:02d}:{ss:02d}.{mss:03d}]"

    # 构建输出
    lines = []
    N = len(merged)
    prev_empty=False
    for i, (o_time, o_text, t_text) in enumerate(merged):
        
        if(o_text.isspace() or (o_text == "")):
            if(prev_empty):
                continue
            prev_empty=True
            lines.append(f"{fmt_ts(o_time)} {o_text}")
            continue
            # print("?")
        else:
            # print("!",o_text,o_text.isspace())
            prev_empty=False

        lines.append(f"{fmt_ts(o_time)} {o_text}")
        
        # print(o_text)

        if i < N - 1:
            next_time = merged[i + 1][0]
        else:
            next_time = o_time + 1000  # 最后一句
        lines.append(f"{fmt_ts(next_time)} {t_text}")

    # return ""
    return "\n".join(lines)
