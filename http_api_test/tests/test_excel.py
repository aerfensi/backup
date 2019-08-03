from unittest import TestCase, skip
from base import excel,logger
import os
import re

curr_dir = os.path.dirname(os.path.abspath(__file__))
testcase_dir = curr_dir[:-5] + 'testcases\\'


class TestExcel(TestCase):
    @skip
    def test_read_sheet(self):
        for i in excel.read_wb(testcase_dir + 'petstore_swagger.xlsx', '工作表1'):
            print(i)

    @skip
    def test_read_wb(self):
        print(excel.read_wb(testcase_dir + 'petstore_swagger.xlsx'))

    @skip
    def test_read_wbs(self):
        data = [(testcase_dir + 'petstore_swagger.xlsx', '工作表1'),
                (testcase_dir + 'petstore_swagger.xlsx', '工作表2','111')]
        print(excel.read_wbs(data))

    def test_t(self):
        url='https://{{pet_name}}/{{pet_id}}'
        props={'pet_id': '12345', 'pet_name': '黄狗'}
        keys=re.findall('{{(.*?)}}',url)
        logger.info('keys='+str(keys))
        for key in keys:
            url=re.sub('{{'+key+'}}',props[key],url)
        logger.info(url)
