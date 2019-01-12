#!/bin/bash 
set -e

function help(){
    echo -e "\033[32m music finder v1.0 \033[0m"
    echo -e "\033[32m <file> : 查找文件      \033[0m"
    echo -e "\033[32m -d <directory> : 查找目录 \033[0m"
    echo -e "\033[32m -h : 显示帮助信息         \033[0m"
    exit 0
}

[ "$1" == "-h" ] || [[ "$1" != "-d" && "$1" =~ ^- ]] || [ "$#" -eq 0 ] || [ "$1" == "-d" -a "$#" -eq 1 ] && help

# 查找时的选项
FILE_TYPE="f"
FILE_NAME="$1"
[ "$1" == "-d" ] && FILE_TYPE="d" && FILE_NAME="$2"

# 电脑中的音乐目录
MUSIC_PATH="/mnt/c/Users/kinux/Music/music"
# ALBUM_PATH 移动硬盘上的专辑目录
[ -d /mnt/e/专辑 ] && ALBUM_PATH="/mnt/e/专辑"
[ -d /mnt/f/专辑 ] && ALBUM_PATH="/mnt/e/专辑"
[ -z "$ALBUM_PATH" ] && echo -e "\033[31m 错误：专辑目录不存在 \033[0m" && exit 1

# 查找结果
FIND_RESULT[0]=""
oldIFS=$IFS
IFS=$'\n'
i=0
for line in $(find "$ALBUM_PATH" -type "$FILE_TYPE" -iname "*$FILE_NAME*")
do 
    printf "\033[32m %-4s $line\n\033[0m" "$i"
    FIND_RESULT[$i]=$line
    i=$((i+1))
done
IFS=$oldIFS
[ -z "${FIND_RESULT[0]}" ] && echo -e "\033[32m 没有查找结果 \033[0m" && exit 0

read -p "输入序号：" index
expr "$index" "+" 1 &> /dev/null || exit 0
[ -z "${FIND_RESULT[$index]}" ] && echo "\033[31m 错误：索引越界 \033[0m" && exit 1

if [ "$FILE_TYPE" == "d" ]
then
    # 列出目录中的文件
    ls --color "${FIND_RESULT[$index]}"
elif [ "$FILE_TYPE" == "f" ]
then
    # 复制文件
    cp -v "${FIND_RESULT[$index]}" "$MUSIC_PATH"
fi
