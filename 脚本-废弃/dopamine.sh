#!/bin/bash

# 转换当前目录下所有 dopamine 保存的播放列表
# 原播放列表：m3u格式、绝对路径
# 新播放列表：m3u格式、相对路径

set -e
mkdir tmp
for file in *.m3u
do
    touch "tmp/$file"
    oldIFS=$IFS
    IFS=$'\n'
    for line in $(cat "$file")
    do
        mp3FileName=${line##*\\}
        echo "$mp3FileName" >> tmp/"$file"
    done
    IFS=$oldIFS
done
