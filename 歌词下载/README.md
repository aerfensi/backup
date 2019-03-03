# README

下载歌词，支持网易云音乐、QQ音乐。  

中文歌的话读一遍歌词也就知道在唱什么了，哪怕是周杰伦的歌。所以我一般只下载外文歌的歌词。  
对于外文歌词，会合并歌词的原文和译文，格式为：`[时间]原文 （译文）`。  

歌词文件保存路径为`~\音乐整理\xxx.lrc`。  
请确保【音乐整理】目录存在。

使用方法：执行lyric_crawler.py脚本即可。

## 查找歌曲id的方法

1. 打开网易云音乐或QQ音乐的网页
1. 搜索需要下载歌词的歌曲
1. 打开该歌曲的网页
1. 从url中找到id

网易云音乐：`https://music.163.com/#/song?id=1338695683` → id=1338695683  
QQ音乐：`https://y.qq.com/n/yqq/song/003ULL5o2D7UMu.html` → id=003ULL5o2D7UMu

## API

### 网易云音乐  

`http://music.163.com/api/song/lyric?os=pc&id=【歌曲id】&lv=-1&kv=-1&tv=-1`  
从网上找的，可以用，但是我自己抓包的时候没看到这个API，网页版用的是weapi，电脑客户端用的是eapi。  
有理由相信这个api是旧版的，但还是可以使用。

`https://api.imjad.cn/cloudmusic/?type=lyric&id=【歌曲id】&br=128000`  
`https://api.imjad.cn/`这个网站提供一些可用的api，包括网易云音乐的，哔哩哔哩的，等等。

### QQ音乐

`https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?callback=MusicJsonCallback_lrc&pcachetime=【当前的时间戳】&songmid=【歌曲的mid】&g_tk=5381&jsonpCallback=MusicJsonCallback_lrc&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0`  
从QQ音乐网页版上抓到的。