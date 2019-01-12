#!/usr/bin/env python3
# coding=utf-8

"""
抓取知乎回答的脚本，总共两种用途
1. 抓取知乎的回答，保存成markdown
2. 抓取回答中的所有图片
"""

import api.zhihu as zhihu
import api.log as log
from argparse import ArgumentParser
from os import makedirs, path
from re import match, sub
from requests import Session
from logging import ERROR


def del_spec_char(string):
    """
    去除字符串中不能在文件名中出现的字符
    """
    return sub(r'[?\\/*<>:"|]', '', string)


def save_answer(meta, answer):
    print('正在保存知乎回答...')
    if args.create:
        answer_dir = del_spec_char(meta['title'])
        try:
            makedirs(answer_dir)
        except FileExistsError:
            log.info('目录（{}）已经存在'.format(answer_dir))
        answer_path = '{}/{} - {}.md'.format(answer_dir, answer_dir, del_spec_char(meta['answerer']))
    else:
        answer_path = '{} - {}.md'.format(del_spec_char(meta['title']), del_spec_char(meta['answerer']))

    with open(answer_path, 'w', encoding='utf-8') as md_file:
        for k, v in meta.items():
            if k == 'avatar':
                md_file.write('![avatar]({})  \n'.format(v))
            elif k == 'title':
                md_file.write('# {}  \n\n'.format(v))
            elif k == 'url':
                md_file.write('[{}]({})  \n'.format(meta['title'], v))
            else:
                md_file.write(v + '  \n')

        md_file.write('\n***\n\n')
        md_file.write(answer)


def save_images(session, meta, urls):
    if not urls:
        print('没有需要下载的图片')
        return
    print('开始下载图片...')
    images_dir = del_spec_char(meta['answerer'])
    if args.create:
        answer_dir = del_spec_char(meta['title'])
    else:
        answer_dir = '.'
    try:
        makedirs('{}/{}'.format(answer_dir, images_dir))
    except FileExistsError:
        log.info('目录（{}/{}）已经存在'.format(answer_dir, images_dir))

    for url in urls:
        with session.get(url, headers=zhihu.get_headers(referer=meta['url']), timeout=5) as resp:
            filename = match(r'.*/(.*\.jpg$)', url).group(1)
            filename = del_spec_char(filename)
            print('正在保存：', filename)
            with open('{}/{}/{}'.format(answer_dir, images_dir, filename), 'wb') as file:
                file.write(resp.content)


def get_args():
    parser = ArgumentParser(prog='zhspider.py', description='Download Zhihui answer')
    parser.add_argument('url')
    parser.add_argument('-c', dest='create', action='store_true', help='create a dir for the question')
    parser.add_argument('-d', dest='down', action='store',
                        choices={'md', 'img', 'both'}, default='md',
                        help='download markdown, images or both')
    return parser.parse_args()


if __name__ == '__main__':
    log.init_default_logger(False,ERROR)
    args = get_args()
    url_type = zhihu.check_url(args.url)
    if url_type == zhihu.URL_TYPE.Answer or url_type == zhihu.URL_TYPE.Article:
        with Session() as session:
            if args.down == 'md':
                meta, answer = zhihu.get_post(session, args.url)
                save_answer(meta, zhihu.html2md(answer))
            elif args.down == 'img':
                meta, urls = zhihu.get_img_urls(session=session, url=args.url)
                save_images(session, meta, urls)
            else:
                meta, answer = zhihu.get_post(session, args.url)
                urls = zhihu.get_img_urls(answer)
                save_answer(meta, zhihu.html2md(answer))
                save_images(session, meta, urls)

    elif url_type == zhihu.URL_TYPE.Question or url_type == zhihu.URL_TYPE.Number:
        print('仅支持用邮箱登录知乎！！！！！')
        with zhihu.ZhihuSpider() as spider:
            if args.down == 'md':
                meta, answer = spider.select_answer(args.url, args.down)
                answer = zhihu.html2md(answer)
                save_answer(meta, answer)
            elif args.down == 'img':
                meta, urls = spider.select_answer(args.url, args.down)
                save_images(spider.session, meta, urls)
            elif args.down == 'both':
                meta, answer, urls = spider.select_answer(args.url, args.down)
                answer = zhihu.html2md(answer)
                save_answer(meta, answer)
                save_images(spider.session, meta, urls)
    else:
        print(args.url, '格式不符合要求')
