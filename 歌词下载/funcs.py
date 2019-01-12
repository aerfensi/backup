import requests
import urllib3
import re

# 不要显示警告，比如不显示忽略SSL证书检验时的警告
urllib3.disable_warnings()

DEBUG = False


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def fetch_base(url: str) -> requests.models.Response:
    response = requests.get(url, verify=False)
    return response


def extract_imjad_nets(response: requests.models.Response) -> (str, str):
    """
    从 https://api.imjad.cn/cloudmusic 中获取的response中提取歌词
    """
    data = response.json()
    # 返回的json字符串最外层为花括号，所以这里的data是一个dict
    # get方法无法在dict中找到对应的key，默认返回None。为了防止报错，第一次调用get时，如果找不到'lrc'，则返回一个空字典
    # 如果response中没有歌词，则返回的是 None，None
    o_lyric = data.get('lrc', {}).get('lyric')
    t_lyric = data.get('tlyric', {}).get('lyric')
    return o_lyric, t_lyric


def merge_lrc(o_lyric: str, t_lyric: str) -> str:
    """
    合并歌词，t_lyric为空，则直接返回o_lyric

    :param o_lyric: 格式正确的歌词原文的字符串。
    :param t_lyric: 格式正确的歌词译文的字符串。
    :returns: 合并后的歌词的字符串，格式为 [时间点]歌词原文 （歌词译文）
    """
    assert o_lyric, '<merge_lrc> error: 无歌词原文 o_lyric'

    if not t_lyric:
        return o_lyric

    o_list = o_lyric.split('\n')
    t_list = t_lyric.split('\n')
    lyric = list()
    # 搜索t_lyric中的元素时的起始下标。
    # 默认为0，即从t_lyric中的第0个元素开始向后搜索
    t_s = 0
    for o_e in o_list:
        o_m = re.match(r'\[(.*?)\].*', o_e)
        if o_m is None:
            continue
        o_t = o_m.group(1)
        # debug(o_t)
        for t_i, t_e in enumerate(t_list[t_s:], start=t_s):
            # debug(t_e)
            t_m = re.match(r'\[(.*?)\](.*)', t_e)
            if t_m is None:
                break
            t_t = t_m.group(1)
            t_c = t_m.group(2)
            if t_t == o_t and len(t_c) != 0 and not t_c.isspace():
                o_e = '{} （{}）'.format(o_e, t_c)
                t_s = t_i
                break
        lyric.append(o_e)
    return '\n'.join(lyric)
