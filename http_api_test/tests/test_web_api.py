import json
import unittest
from base import web_api
from requests_toolbelt.utils import dump

ADD_PET_DATA = {'id': 'petstore_swagger_01', 'name': '添加一个宠物', 'ignore': None, 'method': 'post',
                'url': 'https://petstore.swagger.io/v2/pet', 'params': None,
                'headers': '{"Content-Type":"application/json","Accept":"application/json"}',
                'body': '{"id":12345,"category":{"id":1,"name":"狗"},"name":"黄狗","photoUrls":["string"],"tags":[{"id":1,"name":"黄色"}],"status":"available"}',
                'checkpoint': '“$.id”==”12345”'}

UPDATE_PET_DATA = {'id': 'petstore_swagger_02', 'name': '更新一个宠物', 'ignore': None, 'method': 'post',
                   'url': 'https://petstore.swagger.io/v2/pet/12345', 'params': None,
                   'headers': '{"Content-Type":"application/x-www-form-urlencoded"}', 'body': 'name=%E7%8B%97%E7%8B%97',
                   'checkpoint': None}

GET_PET_DATA = {'id': 'petstore_swagger_03', 'name': '获取一个宠物', 'ignore': None, 'method': 'get',
                'url': 'https://petstore.swagger.io/v2/pet/12345', 'params': None,
                'headers': '{"Accept":"application/json"}', 'body': None, 'checkpoint': None}

UPLOAD_PET_IMG = {'id': 'petstore_swagger_04', 'name': '上传宠物照片', 'ignore': None, 'method': 'post',
                  'url': 'https://petstore.swagger.io/v2/pet/12345/uploadImage', 'params': None,
                  'headers': '{"Content-Type":"multipart/form-data","Accept":"application/json"}',
                  'body': '[ { "name": "additionalMetadata", "file_obj": "dog" }, { "name": "file", "file_name": "res/petstore_swagger_04_dog.jpg", "Content-type": "image/jpeg" } ] ',
                  'checkpoint': None}


class TestWebApi(unittest.TestCase):

    # @unittest.skip
    def test_send_request(self):
        # web_api.send_request(ADD_PET_DATA)
        # web_api.send_request(UPDATE_PET_DATA)
        # web_api.send_request(GET_PET_DATA)
        resp = web_api.send_request(UPLOAD_PET_IMG)
        print(resp.text)
        # 如果上传了二进制文件，data.decode就会失败。
        #data = dump.dump_all(resp)
        #print(data.decode('utf-8'))

    @unittest.skip
    def test_load_multipart(self):
        data = json.loads('[ { "name": "additionalMetadata", "file_obj": "dog" }, { "name": "file", "file_name": "res/petstore_swagger_04_dog.jpg", "Content-type": "image/jpeg" } ]')
        print(web_api.load_multipart(data))
