import json
import os
import re
import sys
import unittest

from ddt import ddt, data

import HtmlTestRunner
from base import *


def gen_tcs_path():
    """
    获取测试用例表格的路径，返回的list的元素可以是wb和sheet的二元组，或者仅包含wb
    :return:[[workbook的路径, sheet的名字],[workbook的路径,]...]
    """
    if len(sys.argv) == 1:
        return [[str(ini.tcs_path / i)] for i in os.listdir(str(ini.tcs_path)) if i.endswith('.xlsx')]

    tcs_path = []
    for i in sys.argv[1:]:
        path = i.split('.')
        path[0] = str(ini.tcs_path / (path[0] + '.xlsx'))
        tcs_path.append(path)
    return tcs_path


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


tcs = excel.read_wbs(gen_tcs_path())


@ddt
class TestApi(unittest.TestCase):
    @data(*tcs)
    def test_api(self, tc):
        logger.info(tc['id'] + ' begin--------------------------------------')
        # 这个影响到测试报告中的测试用例的名字，所以不管是不是skip，都要加id
        self.assertTrue(tc['id'])
        self.id = lambda: tc['id']
        if tc['ignore']:
            self.skipTest(tc['id'] + ' 主动忽略该测试用例')

        # 检查测试用例中基本的一些字段是否存在
        self.assertTrue(tc['name'])
        self.assertTrue(tc['method'])
        self.assertTrue(tc['url'])

        # debug模式下，props从文件中读取
        if ini.debug and ini.props_path.is_file():
            with ini.props_path.open(encoding='utf-8') as file:
                global props
                props = json.load(file)
                logger.debug('从props文件中读取：' + str(props))

        # 将测试用例中填写的属性名替换为对应的属性值
        if tc['url']:
            tc['url'] = key_to_value(tc['url'])
        if tc['headers']:
            tc['headers'] = key_to_value(tc['headers'])
        if tc['body']:
            tc['body'] = key_to_value(tc['body'])
        if not tc['statuscode']:
            tc['statuscode'] = '200'

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
    test_suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestApi)
    if ini.debug:
        unittest.TextTestRunner().run(test_suite)
    else:
        HtmlTestRunner.HTMLTestRunner(report_title=ini.report_title, report_name=ini.report_title,
                                      timestamp=ini.timestamp, combine_reports=True).run(test_suite)

    if mail.check():
        current_log = ini.logs_path / (ini.test_name + '.log')
        current_report = ini.reports_path / (ini.test_name + '.html')
        try:
            mail.zip_attachment([current_log, current_report])
            mail.send()
        finally:
            mail.rm_archive()