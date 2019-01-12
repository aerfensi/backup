#!/usr/bin/env python3
'''
一个简单的 python3 脚本，目的是查找和复制我移动硬盘中存在的音乐文件；同时这也是我写的第一个 python 脚本
如果硬要说这个脚本有什么特色的话，就是它同时适配 Windows 和 Linux
'''
from argparse import ArgumentParser
from shutil import copy
from string import ascii_lowercase
from pathlib import Path
from sys import platform
from os import walk
from os.path import join
from os import listdir
from os import environ

# 参数解析：默认搜索文件，-d 表示搜素目录
def get_args():
    parser = ArgumentParser(prog='mfinder')
    parser.add_argument('-d', dest='dir', action='store_true',help='设置搜索对象的类型为目录')
    parser.add_argument('name',help='被搜索对象的名字')
    return parser.parse_args()

def get_album_path() -> str:
    if platform == 'win32':
        for i in ascii_lowercase:
            album_path=Path(i+':/')/'专辑'
            try:
                if album_path.exists():
                    return str(album_path)
            except PermissionError as error: # 如果访问的设备是Windows下的光驱，会抛出这个异常
                print(error)

    elif platform == 'linux':
        for i in listdir('/media/'+environ['USER']):
            album_path=Path('/media/'+environ['USER'])/i
            if album_path.exists():
                return str(album_path)
    
    else:
        raise SystemExit('错误：不支持的平台！')

def get_music_path() -> str:
    if platform == 'win32':
        music_path=Path.home()/'Music/music'  # 选择pathlib.Path而不是os.path就是因为我要用它的home方法获得主目录
    elif platform == 'linux':
        music_path=Path.home()/'Music'
    else:
        raise SystemExit('错误：不支持的平台！')
    
    if music_path.exists():
        return str(music_path)

def search_file() -> list:
    result=list()
    i = 0
    for path,dirs,files in walk(album_path):
        for element in dirs if args.dir else files:
            if element.find(args.name) >= 0:
                result.append(join(path,element))
                i+=1

    if not result: raise SystemExit('没有搜索结果')
    return result

# 选择对搜索结果的操作
def handle_result(result:list):
    print('')
    i=0
    while i < len(result):
        print('{:<4d}{file}'.format(i, file=result[i]))
        i+=1

    print('')
    index=input('请选择序号：')
    if index and index.isdigit():
        index = int(index)
    else:
        raise SystemExit('错误：输入的不是数字！')
    
    if index < 0 or index >= len(result): raise SystemExit('错误：输入的数字超过界限')
    
    if args.dir:
        for i in listdir(result[index]):
            print(i)
    else:
        print(result[index]+r' --> ' + music_path)
        copy(result[index],music_path)

if __name__ == '__main__':
    album_path=get_album_path()
    music_path=get_music_path()
    if not album_path or not music_path:
        raise SystemExit('错误：没有找到专辑目录或者音乐目录')
    args=get_args()
    handle_result(search_file())