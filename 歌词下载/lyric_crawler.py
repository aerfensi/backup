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
    dir_path = path.join(path.expanduser('~'), '音乐整理')

    def __init__(self, id_: str, source: SOURCE, filename: str):
        """
        :param id_: 抓取歌词的id
        :param source: 抓取歌词的网站
        :param filename: 保存歌词用的文件名
        """
        if source is SOURCE.Nets:
            self.url = Lyric.nets_url.format(id_)
        elif source is SOURCE.Tencent:
            self.url = Lyric.qq_url.format(pcachetime=str(int(time() * 1000)), songmid=id_)
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
        提取歌词，获得response中的歌词原文和歌词译文（如果有的话）。
        如果歌词的格式有问题的话，也需要做格式化的处理。

        :param func: 形如 function(response)->(str,str) 的函数
        """
        print('提取歌词')
        self.o_lyric, self.t_lyric = func(self.response)
        return self

    def merge(self, func):
        """
        合并歌词的原文和译文，如果只有原文的话，最后等到的就是原文。

        :param func: 形如 function(o_lyric:str, t_lyric:str)->str 的函数
        """
        print('合并歌词')
        self.lyric = func(self.o_lyric, self.t_lyric)
        return self

    def output(self, merge_flag):
        """
        写入lyric到文件，若写入失败，则将歌词复制到系统剪切板
        """
        print('输出结果')
        try:
            if merge_flag:
                with open(self.file_path, 'w', encoding='utf-8') as file:
                    file.write(self.lyric)
            else:
                with open(self.file_path+".o", 'w', encoding='utf-8') as o_file:
                    o_file.write(self.o_lyric)
                with open(self.file_path+".t", 'w', encoding='utf-8') as t_file:
                    t_file.write(self.t_lyric)

        except OSError as os_e:
            print(os_e)
            if merge_flag:
                # 复制内容到系统剪切板
                pyperclip.copy(self.lyric)


def print_info():
    info = (
        "输入格式：filename,source,id[,merge]\n"
        "source类型：\n"
        "q：QQ音乐\n"
        "w：网易音乐\n"
        "x：虾米音乐\n"
        "debug：为0，不合并歌词；为其他或不填，合并歌词\n"
        "需要merge标志是因为有些歌词原文译文合并错乱，只能手动合并\n")
    print(info)


def user_in() -> (str, SOURCE, str):
    args = input('请输入: ').split(',')
    assert len(args) > 2, '<user_in> error: 输入参数数量小于3'

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

    merge_flag = True

    if len(args) > 3 and args[3] == "0":
        merge_flag = False

    return id_, src, filename, merge_flag


def main():
    # 我并不把merge_flag作为Lyric对象的成员，因为Lyric中应该只保存歌词的信息，至于歌词是否要合并，由其他代码控制
    id_, src, filename, merge_flag = user_in()
    lrc = Lyric(id_, src, filename)
    print(lrc, '\n')
    if lrc.source == SOURCE.Nets:
        lrc.fetch(fetch_base) \
            .extract(extract_imjad_nets)

    elif lrc.source == SOURCE.Tencent:
        lrc.fetch(fetch_qq) \
            .extract(extract_qq)

    if merge_flag:
        lrc.merge(merge_lrc_timedelta)
    lrc.output(merge_flag)


if __name__ == "__main__":
    print_info()
    while True:
        try:
            main()
        except AssertionError as e:
            print(e)
        except KeyboardInterrupt:
            exit()
