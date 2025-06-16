import urllib.request
import urllib.error
import json

def download_lyrics_by_url(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
        data = json.loads(content)
        lrc = data.get('lrc', {}).get('lyric', '') or ''
        tlrc = data.get('tlyric', {}).get('lyric', '') or ''
        return [lrc, tlrc]
    except Exception as e:
        return ['', '']
