#!/bin/bash

# 运行该文件后，遍历当前目录下的所有zpl文件，生成同名的m3u文件
# 如果同名的m3u文件已存在，原文件会被覆盖

for item in *.zpl
do
    echo "Converting $item"
    name=${item%.zpl}
    name=${name}.m3u
    # printf "#EXTM3U\n" > "$name"
    grep 'src' "$item" | awk 'BEGIN {FS="\""} {print $2 "#" $8 "#" $10 "#" $12}' | while read -r line
    do
        file=$(echo $line | cut -d "#" -f 1)
        file=${file//*\\/}
        file=${file//&amp;/&}
        
        # song=$(echo $line | cut -d "#" -f 2)
    
        # artist=$(echo $line | cut -d "#" -f 3)
        # artist=${artist//&amp;/&}
    
        # duration=$(echo $line | cut -d "#" -f 4)
        # 注释掉的两行是对计算后的播放时常四舍五入
        # 但是这样效率太低，所以我直接取整数，就是下面新增的一行
        #duration=$(echo "scale=2;$duration/1000" | bc)
        #duration=$(printf "%.0f" $duration)
    
        # duration=$(($duration/1000))
    
        # echo "#EXTINF:$duration, $artist - $song" >> "$name"
        echo "$file" >> "$name"
    done
done
