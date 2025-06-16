import json
import http.client
import logging
from typing import Optional

from net_tools import http_download


class SearchResult:
    """ Lyrics that match the metadata to be searched.
    """

    def __init__(self, sourceid, downloadinfo, title='', artist='', album='', comment=''):
        """

        Arguments:
        - `title`: The matched lyric title.
        - `artist`: The matched lyric artist.
        - `album`: The matched lyric album.
        - `downloadinfo`: Some additional data that is needed to download the
          lyric. Normally this value is the url or ID of the lyric.
          ``downloadinfo`` MUST be composed with basic types such as numbers,
          lists, dicts or strings so that it can be converted to D-Bus compatible
          dict with `to_dict` method.
        """
        self._title = title
        self._artist = artist
        self._album = album
        self._comment = comment
        self._sourceid = sourceid
        self._downloadinfo = downloadinfo

    def to_dict(self, ):
        """ Convert the result to a dict so that it can be sent with D-Bus.
        """
        return {'title': self._title,
                'artist': self._artist,
                'album': self._album,
                'comment': self._comment,
                'sourceid': self._sourceid,
                'downloadinfo': self._downloadinfo}


NETEASE_HOST = 'https://music.163.com'
NETEASE_SEARCH_URL = '/api/search/get'
NETEASE_LYRIC_URL  = '/api/song/lyric'

def fetch_lyric_url(title: str, artist: Optional[str] = None, config_proxy=None) -> str:
    """
    根据 song title 和可选的 artist，从网易云接口搜索并返回最优匹配的歌词下载链接。
    如果出错会抛出 HTTPException，或在没有结果时返回空字符串。
    """
    # 1. 构造搜索关键字
    keys = [title]
    if artist:
        keys.append(artist)
    url    = NETEASE_HOST + NETEASE_SEARCH_URL
    urlkey = '+'.join(keys).replace(' ', '+')
    params = f's={urlkey}&type=1'.encode('utf-8')

    # 2. 执行第一次请求
    status, content = http_download(
        url=url,
        method='POST',
        params=params,
    )
    if status < 200 or status >= 400:
        raise http.client.HTTPException(status, "搜索请求失败")

    # 3. 将 JSON 转换为 SearchResult 列表的辅助函数
    def map_song(song) -> SearchResult:
        artist_name = song['artists'][0]['name'] if song.get('artists') else ''
        lyric_url = (
            f"{NETEASE_HOST}{NETEASE_LYRIC_URL}"
            f"?id={song['id']}&lv=-1&kv=-1&tv=-1"
        )
        return SearchResult(
            title=song.get('name', ''),
            artist=artist_name,
            album=song.get('album', {}).get('name', ''),
            sourceid='netease',
            downloadinfo=lyric_url
        )

    parsed = json.loads(content.decode('utf-8'))
    result = [map_song(s) for s in parsed.get('result', {}).get('songs', [])]

    # 4. 如果结果超过 10 条，执行第二页请求
    song_count = parsed.get('result', {}).get('songCount', 0)
    if song_count > 10:
        params = f"{urlkey}&type=1&offset=10".encode('utf-8')
        status, content = http_download(
            url=url,
            method='POST',
            params=params,
        )
        if status < 200 or status >= 400:
            raise http.client.HTTPException(status, "第二页请求失败")
        parsed2 = json.loads(content.decode('utf-8'))
        result += [map_song(s) for s in parsed2.get('result', {}).get('songs', [])]

    # 5. 按 title 完全匹配优先排序
    try:
        target = title.strip().lower()
        exact   = [r for r in result if r._title.strip().lower() == target]
        others  = [r for r in result if r._title.strip().lower() != target]
        result  = exact + others
    except Exception as e:
        logging.warning("排序 SearchResult 时失败: %s", e)

    # 6. 返回第一个的 downloadinfo，如果没有结果返回空
    if result:
        return result[0]._downloadinfo
    return ""