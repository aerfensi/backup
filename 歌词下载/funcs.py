import requests
import urllib3
import re
import json
from base64 import b64decode
from datetime import datetime

# 不要显示警告，比如不显示忽略SSL证书检验时的警告
urllib3.disable_warnings()

DEBUG = False


def debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def fetch_base(url: str) -> requests.models.Response:
    return requests.get(url, verify=False)


def fetch_qq(url: str) -> requests.models.Response:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0',
        'Host': 'c.y.qq.com',
        'Referer': 'https://y.qq.com/portal/player.html',
        'DNT': '1',
        'TE': 'Trailers'
    }
    return requests.get(url, headers=headers, verify=False)


def extract_imjad_nets(response: requests.models.Response) -> (str, str):
    """
    从 https://api.imjad.cn/cloudmusic 中获取的response中提取歌词
    """
    assert response.status_code == 200, '<extract_imjad_nets> error: response.status_code != 200'
    data = response.json()
    # 返回的json字符串最外层为花括号，所以这里的data是一个dict
    # get方法无法在dict中找到对应的key，默认返回None。为了防止报错，第一次调用get时，如果找不到'lrc'，则返回一个空字典
    # 如果response中没有歌词，则返回的是 None，None
    o_lyric = data.get('lrc', {}).get('lyric')
    t_lyric = data.get('tlyric', {}).get('lyric')
    return o_lyric, t_lyric


def extract_qq(response: requests.models.Response) -> (str, str):
    assert response.status_code == 200, '<extract_qq> error: response.status_code != 200'
    data = json.loads(re.search(r'\{.*\}', response.text).group())
    o_lyric = b64decode(data.get('lyric').encode('utf8')).decode('utf8') if data.get('lyric') else None
    t_lyric = b64decode(data.get('trans').encode('utf8')).decode('utf8') if data.get('trans') else None
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
    # t_ 歌词译文，s，start，开始搜索的位置；t，time；m，match，正则匹配结果；c，content，歌词内容
    # 默认为0，即从t_lyric中的第0个元素开始向后搜索
    t_s = 0
    for o_e in o_list:
        o_m = re.match(r'\[(.*?)\].*', o_e)
        if o_m is None:
            continue
        # 将 MM:SS.f以及MM:SS.ff的时间格式补全为MM:SS.fff
        # 原因是歌词原文和译文的时间格式可能不同
        o_t = '{:0<9}'.format(o_m.group(1))
        # debug(o_t)
        for t_i, t_e in enumerate(t_list[t_s:], start=t_s):
            # debug(t_e)
            t_m = re.match(r'\[(.*?)\](.*)', t_e)
            if t_m is None:
                continue
            t_t = '{:0<9}'.format(t_m.group(1))
            t_c = t_m.group(2)
            if t_t == o_t and len(t_c) != 0 and not t_c.isspace():
                m_r = '{} （{}）'.format(o_e, t_c)
                t_s = t_i
                break
        else:
            m_r = o_e
        lyric.append(m_r)
    return '\n'.join(lyric)


def merge_lrc_timedelta(o_lyric: str, t_lyric: str) -> str:
    """
    合并歌词，t_lyric为空，则直接返回o_lyric。
    歌词译文中找不到与歌词原文时间相同的歌词，则从译文中寻找一条时间差小于2秒，且最接近原文时间的歌词。

    :param o_lyric: 格式正确的歌词原文的字符串。
    :param t_lyric: 格式正确的歌词译文的字符串。
    :returns: 合并后的歌词的字符串，格式为 [时间点]歌词原文 （歌词译文）
    """
    assert o_lyric, '<merge_lrc> error: 无歌词原文 o_lyric'

    if not t_lyric:
        return o_lyric

    o_list = [i.strip() for i in o_lyric.split('\n')]
    t_list = [i.strip() for i in t_lyric.split('\n')]
    lyric = list()

    # 歌词译文中的搜索结果search_result
    rr = None
    # 歌词译文中的搜索结果的暂存区，存入的元素格式为 (delta_time,lyric_content,content_index)
    stage = list()
    t_s = 0
    for o_e in o_list:
        rr = None
        stage.clear()
        o_m = re.match(r'\[(\d{2}:\d{2}\.\d{2,3})\](.+)', o_e)
        if o_m is None:
            continue
        o_t = datetime.fromisoformat('2019-01-01:00:{:0<9}'.format(o_m.group(1)))
        debug('<merge_lrc_timedelta> t_s =', t_s)
        for t_i, t_e in enumerate(t_list[t_s:], start=t_s):
            t_m = re.match(r'\[(\d{2}:\d{2}\.\d{2,3})\](.+)', t_e)
            if t_m is None:
                continue
            t_t = datetime.fromisoformat('2019-01-01:00:{:0<9}'.format(t_m.group(1)))
            delta_time = (o_t - t_t).total_seconds()
            if delta_time == 0:
                rr = t_m.group(2)
                t_s = t_i
                break
            elif 2 > delta_time > -2:
                stage.append((delta_time, t_m.group(2), t_i))
            elif delta_time < -2:
                break
        if rr is None and stage:
            rr = min(stage, key=lambda i: abs(i[0]))
            t_s = rr[2]
            lyric.append('{} （{}）'.format(o_e, rr[1]))
        elif rr is None and not stage:
            lyric.append(o_e)
        elif rr:
            lyric.append('{} （{}）'.format(o_e, rr))
    return '\n'.join(lyric)
