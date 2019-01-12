#!/usr/bin/env python3
# coding=utf-8

"""
抓取知乎回答的API，返回的全是文本，如果是图片，就返回该图片的url
"""

from requests import Session
from http.cookiejar import LWPCookieJar
from time import time
import api.log as log
from PIL import Image
from io import BytesIO
from enum import Enum
from urllib.parse import urlparse
from re import match, sub, finditer
from html2text import html2text
from lxml import etree
from collections import OrderedDict
from os.path import expanduser, join
from os import mkdir
import json


def get_headers(referer=None):
    headers = {
        # 'Referer': 'https://www.zhihu.com/',
        'User-Agent': (
            r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            r'(KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'
        )
    }
    if referer:
        headers['Referer'] = referer

    return headers


URL_TYPE = Enum('URL_TYPE', ('Answer', 'Question', 'Number', 'Article'))


def check_url(url: str):
    if url.isdigit():
        return URL_TYPE.Number

    urlstruct = urlparse(url)
    log.debug('hostname: ' + urlstruct.hostname)
    log.debug('path: ' + urlstruct.path)
    if urlstruct.hostname == 'www.zhihu.com':
        if match(r'/question/\d+/answer/\d+/?', urlstruct.path):
            return URL_TYPE.Answer
        elif match(r'/question/\d+/?', urlstruct.path):
            return URL_TYPE.Question
    if urlstruct.hostname == 'zhuanlan.zhihu.com' and match(r'/p/\d+/?', urlstruct.path):
        return URL_TYPE.Article


def get_post(session, url):
    type = check_url(url)
    if type == URL_TYPE.Answer:
        return get_answer(session, url)
    elif type == URL_TYPE.Article:
        return get_article(session, url)
    raise SystemExit('格式不符合要求 '+url)


def get_answer(session, url):
    """
    返回的对象结构是
    (
        {
            'title':      # 问题题目
            'url':        # 问题网址
            'avatar':     # 答主头像的链接
            'answerer':   # 答主的名字
            'signature':  # 答主的个性签名
        },
        ''                   # 包含回答内容的HTML格式字符串
    )
    或者是 None
    """
    print('正在获取知乎回答...')
    resp = session.get(url, headers=get_headers(), timeout=5)
    if resp.status_code != 200:
        raise SystemExit('无法链接到指定的URL status_code == '+resp.status_code)

    tree = etree.HTML(resp.text)
    meta = OrderedDict()
    meta['title'] = tree.xpath('//h1[@class="QuestionHeader-title"]/text()')[0]
    meta['url'] = url
    print('问题：', meta['title'])
    meta['avatar'] = tree.xpath('//img[@class="Avatar AuthorInfo-avatar"]')[0].get('src')
    # 匿名用户与非匿名用户是不同的，所以这么写
    meta['answerer'] = next(filter(lambda i: match(r'\S+$', i),
                                   tree.xpath('//span[@class="UserLink AuthorInfo-name"]//text()')))
    print('答主：', meta['answerer'])
    if meta['answerer'] != '匿名用户':
        meta['signature'] = tree.xpath('//div[@class="RichText AuthorInfo-badgeText"]')[0].text
    answer = tree.xpath('//div[@class="RichContent-inner"]')[0]
    answer = etree.tostring(answer, pretty_print=True, method="html", encoding='utf-8').decode('utf-8')
    return meta, answer


def get_article(session, url):
    print('正在获取知乎文章...')
    resp = session.get(url, headers=get_headers(), timeout=5)
    if resp.status_code != 200:
        raise SystemExit('无法链接到指定的URL status_code == '+resp.status_code)

    tree = etree.HTML(resp.text)
    meta = OrderedDict()
    meta['title'] = tree.xpath('//h1[@class="Post-Title"]')[0].text
    meta['url'] = url
    print('专栏文章标题：', meta['title'])
    meta['avatar'] = tree.xpath("//img[contains(concat(' ', @class, ' '), ' Avatar ')]")[0].get('src')
    meta['answerer'] = tree.xpath('//a[@class="UserLink-link"]/text()')[0]
    print('专栏名字：', meta['answerer'])
    answer = tree.xpath("//div[contains(concat(' ', @class, ' '), ' Post-RichText ')]")[0]
    answer = etree.tostring(answer, pretty_print=True, method="html", encoding='utf-8').decode('utf-8')
    return meta, answer


def html2md(html: str):
    # html转成md后，还有些问题，需要再修改
    tmp1 = sub(r'!?\[\]\((?!http).*?\)', '', html2text(html))
    tmp2 = sub(r'\n', r'  \n', tmp1)
    tmp3 = sub(r'(!?\[\]\(http.*?\))', r'  \n\1  \n', tmp2)
    return tmp3


def get_img_urls(text: str = None, session=None, url: str = None):
    print('正在获取图片链接...')
    if text:
        # 知乎上的图片以_r结尾的是原图，_hd是压缩后的图片
        # 但是有些图片是只有hd，没有r的，对于这种图片我是直接放弃不抓取的
        return [i.group() for i in finditer(r'https.*?_r\.jpg', text)]

    if session and url:
        meta, answer = get_post(session, url)
        return meta, set([i.group() for i in finditer(r'https[^"]*?_r\.jpg', answer)])


class ZhihuSpider():
    _PROFILE_URL = 'https://www.zhihu.com/settings/profile'
    _LOGIN_EMAIL_URL = 'https://www.zhihu.com/login/email'
    _HOME = join(expanduser('~'), 'zhspider_files')

    # 我是用邮箱登录的，所以这个先不管
    # LOGIN_PHONE_URL = 'http://www.zhihu.com/login/phone_num'
    # https://www.zhihu.com/api/v4/questions/36064666/answers?sort_by=default&include=data[*].is_normal&limit=5&offset=0

    def __init__(self, cookie_name='default_cookie'):
        try:
            mkdir(ZhihuSpider._HOME)
        except FileExistsError:
            log.warn('目录 {} 已经存在'.format(ZhihuSpider._HOME))

        self.session = Session()
        self.session.cookies = LWPCookieJar(filename=join(ZhihuSpider._HOME, cookie_name))

    def __enter__(self):
        try:
            self.session.cookies.load(ignore_discard=True, ignore_expires=True)
        except Exception:
            print('cookie文件不存在，请登录知乎！')
            log.warn('cookie文件不存在，无法加载！')

        if not self.islogin():
            log.info('登录知乎：{}'.format(self.login()))

        return self

    def __exit__(self, type, value, traceback):
        self.session.close()

    def islogin(self):
        log.debug('islogin')
        resp = self.session.get(ZhihuSpider._PROFILE_URL,
                                headers=get_headers(), allow_redirects=False, timeout=10)
        log.debug('status_code == ' + str(resp.status_code))
        if resp.status_code == 200:
            return True
        else:
            return False

    def login(self) -> bool:
        # 密码是明文的，目前我没找到用*代替密码显示的，同时适用于win和Linux的方法
        data = {'email': input('登录邮箱：'),
                'password': input('登录密码：'),
                'remember_me': 'true',
                'captcha': self.get_captcha()}
        try:
            response = self.session.post(ZhihuSpider._LOGIN_EMAIL_URL,
                                         headers=get_headers(), data=data, timeout=5)
            self.session.cookies.save(ignore_discard=True, ignore_expires=True)
            if response.status_code == 200:
                return True
        except Exception as e:
            print('登录知乎失败！',e.__doc__)
        return False

    def get_captcha(self) -> str:
        captcha_url = 'http://www.zhihu.com/captcha.gif?r={}&type=login'.format(
            time() * 1000)
        captcha_data = self.session.get(
            captcha_url, headers=get_headers()).content
        with Image.open(BytesIO(captcha_data)) as pic:
            pic.show()
            captcha_str = input('请输入验证码：')
        return captcha_str

    def get_answers(self, string, content=False, limit=5, offset=0):
        """
        获取知乎问题中所有回答的API
        默认是从0开始获取5个回答，并且不要这些回答的内容，只要答主信息

        :param string: 问题的url或者是id
        :param content: 是否要求返回回答内容，False只会返回答主的一些个人信息
        """
        log.debug('get_answers')
        if check_url(string) == URL_TYPE.Number:
            id = string
        elif check_url(string) == URL_TYPE.Question:
            id = match(r'/question/(\d+)/?', urlparse(string).path).group(1)
        else:
            raise ValueError('非法的url')

        api_url = ('https://www.zhihu.com/api/v4/questions/{id}/answers?'
                   'sort_by=default&include=data[*].is_normal{content}'
                   '&limit={limit}&offset={offset}').format(id=id, content=',content' if content else '',
                                                            limit=limit, offset=offset)
        log.debug('api_url == ' + api_url)
        resp = self.session.get(api_url, headers=get_headers(), timeout=5)
        log.debug(resp.status_code)
        if resp.status_code == 200:
            return json.loads(resp.text, encoding='utf-8')

    def select_answer(self, string, type):
        """
        每次5个，列出该问题下答主的名字
        按下回车键，继续列出后面的答主名字；ctrl c，退出程序
        选择序号后，返回该答主的答案

        :type md, img 或者 both
        """
        log.debug('choice_answer')
        offset = 0
        try:
            while True:
                data = self.get_answers(string, offset=offset)
                if offset >= data['paging']['totals']:
                    break
                for i, value in enumerate(data['data'], start=offset):
                    print(i, value['author']['name'])
                index = input('选择序号：')
                if index.isdigit():
                    answer = self.get_answers(string, True, 1, int(index))['data'][0]
                    meta = OrderedDict()
                    meta['title'] = answer['question']['title']
                    print('问题：',meta['title'])
                    meta['url'] = 'https://www.zhihu.com/question/{}/answer/{}'.format(answer['question']['id'],
                                                                                       answer['id'])
                    log.debug('url: ' + meta['url'])
                    meta['avatar'] = answer['author']['avatar_url']
                    log.debug('avatar: ' + meta['avatar'])
                    meta['answerer'] = answer['author']['name']
                    print('答主：',meta['answerer'])
                    if type == 'md':
                        return meta, answer['content']
                    elif type == 'img':
                        return meta, get_img_urls(answer['content'])
                    elif type == 'both':
                        return meta, answer['content'], get_img_urls(answer['content'])
                    else:
                        return
                offset += len(data['data'])
        except KeyboardInterrupt:
            raise SystemExit('KeyboardInterrupt')
