import urllib.request
import urllib.error

def http_download(url, method='GET', params=None, proxy=None):
    """
    发起一次 HTTP/HTTPS 请求，并返回 (status, content_bytes)。

    :param url: 请求的完整 URL，示例: "https://music.163.com/api/search/get"
    :param method: 请求方法，"GET" 或 "POST"
    :param params: POST 时发送的 payload，类型为 bytes；GET 时应为 None
    :param proxy: 可忽略，不做处理
    :return: (status_code: int, response_body: bytes)
    """
    # 构造 Request 对象
    req = urllib.request.Request(url, data=params, method=method.upper())
    # 如果是 POST，设置 form 类型
    if method.upper() == 'POST':
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')

    try:
        with urllib.request.urlopen(req) as resp:
            status = resp.getcode()       # HTTP 状态码
            content = resp.read()         # 返回的二进制内容
    except urllib.error.HTTPError as e:
        status = e.code
        content = e.read()
    except Exception as e:
        raise

    return status, content