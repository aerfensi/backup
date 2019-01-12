#!/bin/bash
# 发生错误后停下脚本，这里的错误不包括判断中的假
set -e
if [ ! -d /mnt/"$1"/music ]
then
    echo -e "\033[31m ${1} 盘中不存在备份文件夹 \033[0m"
    exit 1
fi
count=0;
for file in /mnt/c/Users/kinux/Music/MP3文件/*.mp3
do  
    name=${file##*\/}
    backup=/mnt/"$1"/music/"$name"
    if [ ! -e "$backup" ]
    then
        count=$(($count+1))
        echo "正在复制 $name"
        cp -i "$file" "$backup"
    fi
done
echo -e "\033[32m 复制完毕，共计 $count 个文件 \033[0m"
