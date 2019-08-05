from unittest import TestCase, skip
from base import result, props
import json


class TestCheckResult(TestCase):

    @skip
    def test_get_by_jsonpath(self):
        checkpoint = '$.id==12345'
        illusts_len = result.get_by_json_path(checkpoint, self.json_str)
        self.assertEqual(illusts_len, 30)

    # @skip
    def test_parse_check_point(self):
        checkpoint = '$.id =~ 12345'
        a, b, c = result.parse_check_point(checkpoint)
        print(a, b, c, sep='\n')

    @skip
    def test_check(self):
        checkpoint = '$.id==1\n$.name=="黄狗"'
        json_str = {"id": None, "category": {"id": 0, "name": "狗"}, "name": "黄狗", "photoUrls": ["string"],
                    "tags": [{"id": 1, "name": "黄色"}], "status": "available"}
        print(result.check(json_str, checkpoint))

    @skip
    def test_set_props(self):
        setprops = '"pet_id"="$.id"\n"pet_name"="$.name"'
        json_obj = json.loads(
            '{"id":12345,"category":{"id":0,"name":"狗"},"name":"黄狗","photoUrls":["string"],"tags":[{"id":1,"name":"黄色"}],"status":"available"}')
        props['pet_id'] = '-333'
        result.set_props(json_obj, setprops)
        print(props)
