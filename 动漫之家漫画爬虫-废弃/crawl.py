from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from collections import namedtuple
from os import mkdir, environ
from os.path import isdir, join
import aiohttp
import asyncio
from pyquery import PyQuery
from pprint import pprint
import re


def del_spec_char(string):
    """
    去除字符串中不能在文件名中出现的字符
    """
    return re.sub(r'[?\\/*<>:"|]', '', string)


ComicInfo = namedtuple('ComicInfo', 'title,author,link')


def search_comics(driver) -> ComicInfo:
    url = 'https://manhua.dmzj.com/tags/search.shtml?s=' + input('请输入漫画名字：')
    driver.get(url)
    l = []
    for i, j in zip(
            driver.find_elements_by_css_selector(
                'div.tcaricature_block.tcaricature_block2>ul>li>a'),
            driver.find_elements_by_css_selector(
                'div.tcaricature_block.tcaricature_block2>ul>li>div.adiv2hidden:first-child'
            )):
        l.append(
            ComicInfo(
                del_spec_char(i.get_attribute('title')),
                j.get_attribute('innerText'), i.get_attribute('href')))
    return l


def create_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_experimental_option(
        'prefs', {'profile.managed_default_content_settings.images': 2})
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(5)
    return driver


VolInfo = namedtuple('VolInfo', 'title,link,pages')


def get_vols(driver, url):
    driver.get(url)
    vols = []
    for e in driver.find_elements_by_css_selector(
            '.cartoon_online_border>ul>li>a'):
        vols.append({
            'title': e.get_attribute('innerText'),
            'link': e.get_attribute('href')
        })
    for i in range(len(vols)):
        driver.get(vols[i]['link'])
        pages = {}
        for e in driver.find_elements_by_css_selector('#page_select>option'):
            value = e.get_attribute('value')
            pages.update({
                re.match(r'.*/(.*\.jpg)', value).group(1):
                'https:' + value
            })
        print('获取 ', vols[i]['title'])
        yield VolInfo(vols[i]['title'], vols[i]['link'], pages)


async def down(vol, path):
    vol_dir = join(path, vol.title)
    if not isdir(vol_dir):
        mkdir(vol_dir)
    headers = {
        'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36',
        'Referer':
        vol.link
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        for item in vol.pages.items():
            print('正在下载', vol.title, item[0])
            with open(join(vol_dir, item[0]), 'wb') as img_file:
                async with session.get(item[1]) as resp:
                    img_file.write(await resp.read())
    print('下载完毕', vol.title)


def next_future(vols, path, loop):
    try:
        vol = next(vols)
        future = asyncio.ensure_future(down(vol, path))
        future.add_done_callback(lambda _: next_future(vols, path, loop))
    except StopIteration:
        if loop.is_running():
            for t in asyncio.Task.all_tasks():
                if not t.done():
                    return
            print('stop loop')
            loop.stop()


def main():
    driver = create_driver()
    try:
        comics = search_comics(driver)
        for i, v in enumerate(comics):
            print(
                '序号：' + str(i),
                '标题：' + v.title,
                v.author + '\n',
                sep='\n')
        index = int(input('请选择：'))
        comic_dir = join(environ['HOME'], comics[index].title)
        if not isdir(comic_dir):
            mkdir(comic_dir)
        vols = get_vols(driver, comics[index].link)
        loop = asyncio.get_event_loop()
        for _ in range(5):
            next_future(vols, comic_dir, loop)
        loop.run_forever()
    finally:
        loop.close()
        print('结束，退出chrome')
        driver.quit()


if __name__ == '__main__':
    main()
