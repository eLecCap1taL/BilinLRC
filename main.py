from search_lyrics import fetch_lyric_url
from download_lyrics import download_lyrics_by_url

from merge_lyrcis import merge_lrc
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple

DATA_DIR = "data"
GEN_DIR = "gen"
os.makedirs(GEN_DIR, exist_ok=True)

LRC_FILENAME_RE = re.compile(r"^(.+?)-(.+?)\.lrc$")

def process_file(artist: str, title: str, filename: str):
    try:
        url = fetch_lyric_url(title, artist)
        s, ts = download_lyrics_by_url(url)
        merged = merge_lrc(s, ts)
        out_path = os.path.join(GEN_DIR, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(merged)
        print(f"[✓] 生成: {filename}")
    except Exception as e:
        print(f"[✗] 失败: {filename} - {e}")

def main():
    tasks = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        for fname in os.listdir(DATA_DIR):
            if not fname.endswith(".lrc"):
                continue
            match = LRC_FILENAME_RE.match(fname)
            if not match:
                continue
            artist, title = match.groups()
            task = executor.submit(process_file, artist.strip(), title.strip(), fname)
            tasks.append(task)

        for future in as_completed(tasks):
            pass  # 所有打印都在 process_file 中处理了

if __name__ == "__main__":
    main()
