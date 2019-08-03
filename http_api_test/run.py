import os
import re
import sys
import traceback
import unittest

from ddt import ddt, data

import HtmlTestRunner
from base import *


def gen_tcs_path():
    """
    获取测试用例表格的路径，返回的list的元素可以是wb和sheet的二元组，或者仅包含wb
    :return:[[workbook的路径, sheet的名字],[workbook的路径,]...]
    """
    # run.py不会被其他模块导入，所以可以直接使用相对路径，不会报错
    tcs_dir = "testcases/"
    if len(sys.argv) == 1:
        return [[tcs_dir + i] for i in os.listdir(tcs_dir) if i.endswith('.xlsx')]

    tcs_path = []
    for i in sys.argv[1:]:
        path = i.split('.')
        path[0] = tcs_dir + path[0] + '.xlsx'
        tcs_path.append(path)
    return tcs_path


tcs = excel.read_wbs(gen_tcs_path())


def key_to_value(text):
    """
    用props中的键值对替换text中同名的属性。
    如果text中有文本{{id}}，props中有id='100'，则text中的{{id}}会被替换成100。
    """
    if not len(props):
        return text
    keys = re.findall('{{(.*?)}}', text)
    logger.info('keys=' + str(keys))
    for key in keys:
        text = re.sub('{{' + key + '}}', props[key], text)
    logger.info(text)
    return text


@ddt
class TestApi(unittest.TestCase):
    @data(*tcs)
    def test_api(self, tc):
        logger.info(tc['id'] + ' begin--------------------------------------')
        # 检查测试用例中基本的一些字段是否存在
        self.assertTrue(tc['id'])
        self.id = lambda: tc['id']
        self.assertTrue(tc['name'])
        self.assertTrue(tc['method'])
        self.assertTrue(tc['url'])

        # 将测试用例中填写的属性名替换为对应的属性值
        if tc['url']:
            tc['url'] = key_to_value(tc['url'])
        if tc['headers']:
            tc['headers'] = key_to_value(tc['headers'])
        if tc['body']:
            tc['body'] = key_to_value(tc['body'])
        if not tc['statuscode']:
            tc['statuscode'] = '200'

        if tc['ignore'] is not None:
            self.skipTest(tc['id'] + ' 主动忽略该测试用例')
        resp = web_api.send_request(tc)
        logger.info('status code = {}\nreason = {}\nresp body = \n{}'.format(resp.status_code, resp.reason, resp.text))
        self.assertEqual(str(resp.status_code), tc['statuscode'],
                         'status code {} != {}'.format(str(resp.status_code), tc['statuscode']))
        if resp.text:
            if tc['setprops']:
                result.set_props(resp.json(), tc['setprops'])
            if tc['checkpoints']:
                ok, msg = result.check(resp.json(), tc['checkpoints'])
                self.assertTrue(ok, msg)


if __name__ == '__main__':
    try:
        ini.read()
    except (KeyError, ValueError):
        logger.error('配置文件读取失败！')
        logger.error(traceback.format_exc())
        raise SystemExit()
    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestApi)
    HtmlTestRunner.HTMLTestRunner(report_title=ini.report_title).run(test_suite)
