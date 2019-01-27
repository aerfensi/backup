from enum import Enum
from os import path
from funcs import *
from time import time
import pyperclip

SOURCE = Enum('Source', {'Nets': '网易', 'Tencent': '腾讯'})


class Lyric:
    nets_url = 'https://api.imjad.cn/cloudmusic/?type=lyric&id={}&br=128000'
    qq_url = ('https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?'
              'callback=MusicJsonCallback_lrc'
              '&pcachetime={pcachetime}'
              '&songmid={songmid}'
              '&g_tk=5381'
              '&jsonpCallback=MusicJsonCallback_lrc'
              '&loginUin=0'
              '&hostUin=0'
              '&format=jsonp'
              '&inCharset=utf8'
              '&outCharset=utf-8'
              '&notice=0'
              '&platform=yqq'
              '&needNewCode=0')
    dir_path = path.join(path.expanduser('~'), r'Downloads\歌词')

    def __init__(self, id: str, source: SOURCE, filename: str):
        """
        :param id: 抓取歌词的id
        :param source: 抓取歌词的网站
        :param filename: 保存歌词用的文件名
        """
        if source is SOURCE.Nets:
            self.url = Lyric.nets_url.format(id)
        elif source is SOURCE.Tencent:
            self.url = Lyric.qq_url.format(pcachetime=str(int(time() * 1000)), songmid=id)
        self.source = source
        self.file_path = path.join(Lyric.dir_path, filename)
        self.response = None
        self.lyric = None
        self.o_lyric = None
        self.t_lyric = None

    def __str__(self):
        return ' url: {}\n source: {}\n filename: {}'.format(self.url, self.source, self.file_path)

    def fetch(self, func):
        """
        抓取歌词

        :param func: 形如 function(url:str)->response 的函数
        """
        print('抓取歌词')
        self.response = func(self.url)
        return self

    def extract(self, func):
        """
        提取歌词，获得response中的歌词原文和歌词译文（如果有的话）

        :param func: 形如 function(response)->(str,str) 的函数
        """
        print('提取歌词')
        self.o_lyric, self.t_lyric = func(self.response)
        return self

    def format(self, func):
        """
        对歌词做格式化处理，如果有翻译歌词的话，也要合并原文及翻译。

        :param func: 形如 function(o_lyric:str, t_lyric:str)->str 的函数
        """
        print('格式化歌词')
        self.lyric = func(self.o_lyric, self.t_lyric)
        return self

    def output(self):
        """
        写入lyric到文件，若写入失败，则将歌词复制到系统剪切板
        """
        print('输出结果')
        try:
            with open(self.file_path, 'w', encoding='utf-8') as file:
                file.write(self.lyric)
        except OSError as os_e:
            print(os_e)
            # 复制内容到系统剪切板
            pyperclip.copy(self.lyric)


def print_info():
    info = (
        "输入格式：filename,source,id\n"
        "source类型：\n"
        "q：QQ音乐\n"
        "w：网易音乐\n"
        "x：虾米音乐\n")
    print(info)


def user_in() -> (str, SOURCE, str):
    try:
        args = input('请输入: ').split(',')
    except KeyboardInterrupt:
        exit()

    assert len(args) == 3, '<user_in> error: 输入参数数量不为3'

    id_ = args[2].strip()
    debug(id_)

    src = args[1].strip()
    debug(src)
    if src == 'w':
        assert id_.isdigit(), '<user_in> error: 输入的id不是数字'
        src = SOURCE.Nets
    elif src == 'q':
        src = SOURCE.Tencent
    else:
        raise AssertionError('<user_in> error: 输入的source不支持')

    filename = args[0].strip() + '.lrc'
    debug(filename)
    return id_, src, filename


def main():
    id_, src, filename = user_in()
    lrc = Lyric(id_, src, filename)
    print(lrc, '\n')
    if lrc.source == SOURCE.Nets:
        lrc.fetch(fetch_base) \
            .extract(extract_imjad_nets) \
            .format(merge_lrc) \
            .output()
    elif lrc.source == SOURCE.Tencent:
        lrc.fetch(fetch_qq) \
            .extract(extract_qq) \
            .format(merge_lrc) \
            .output()


if __name__ == "__main__":
    print_info()
    while True:
        try:
            main()
        except AssertionError as e:
            print(e)
