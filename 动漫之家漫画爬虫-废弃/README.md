# README

**已经废弃，漫画分辨率太低**

selenium + headless chrome + aiohttp + pyquery

简单的[动漫之家](https://manhua.dmzj.com/)漫画爬虫。  

## 用法

`pip install selenium aiohttp pyquery`

另需安装chrome和chromedriver

`python crawl.py`

效果如下：

请输入漫画名字：灌篮高手  
序号：0  
标题：篮球飞人  
作者:井上雄彦  

序号：1  
标题：灌篮高手剧场版  
作者:井上雄彦  

序号：2  
标题：灌篮高手全国大赛篇(全彩版本)  
作者:井上雄彦  

请选择：2  

## 测试环境

Ubuntu 18.04 x64  
Python 3.6.5  

### 测试所用漫画

漫画                           | 测试时共有几话
-------------------------------|---------------
君主·埃尔梅罗Ⅱ世事件簿        | 共9话
表里一体                       | 共1话
灌篮高手全国大赛篇(全彩版本)   | 共80话 

## 关于这个脚本

文件的写入是同步的，如果需要改成异步的可以使用现成的[aiofiles](https://github.com/Tinche/aiofiles)，当然也可以自己实现

selenium拿到图片的网址，由aiohttp下载。有些漫画有几百话之多，为了防止selenium在获取图片网址的时候花费大量时间，让人怀疑脚本是不是卡住了，所以获取脚本的函数写成生成器函数。缺点是，只要脚本不结束，selenium不会退出，headless chrome也会一直在

最多5个coroutine同时存在，每个coroutine结束后，通过回调函数创建新的coroutine