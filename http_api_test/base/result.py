import jsonpath2
import re
from base import logger, props

"""
检查http response的body是否符合测试用例表格中填写的checkpoint。
这么短的代码要分成多个函数来写的原因是，测试用例中的checkpoint可以随便乱填，容易出现各种错误，把各部分的代码分开，方便将来出问题的时候调试。
"""


def get_by_jsonpath(jsonpath: str, json_obj):
    result = [i.current_value for i in jsonpath2.match(jsonpath, json_obj)]
    return result[0] if len(result) == 1 else result


def parse_check_point(checkpoint: str):
    result = re.match(r'(.*)=([=~])(.*)', checkpoint)
    return result.group(1).strip(), result.group(2).strip(), result.group(3).strip()


def check(json_obj, checkpoints: str):
    """
    :return: check_result, error_msg
    """
    logger.info('json_obj={}'.format(str(json_obj)))
    for checkpoint in checkpoints.split('\n'):
        logger.info('checkpoint={}'.format(checkpoint))
        jsonpath, operator, expectation = parse_check_point(checkpoint)
        logger.info('jsonpath={}, operator={}, expectation={}'.format(str(jsonpath), str(operator), str(expectation)))
        value_by_jsonpath = get_by_jsonpath(jsonpath, json_obj)
        logger.info('value_by_jsonpath = {}'.format(str(value_by_jsonpath)))

        if operator == '=':
            if type(value_by_jsonpath) != type(eval(expectation)):
                return False, '{} != {}'.format(str(type(value_by_jsonpath)), str(type(eval(expectation))))
            if value_by_jsonpath != eval(expectation):
                return False, '{} != {}'.format(str(value_by_jsonpath), str(eval(expectation)))
        elif operator == '~':
            if not isinstance(value_by_jsonpath, str):
                return False, '{}不是字符串类型'.format(str(value_by_jsonpath))
            if not re.search(expectation, value_by_jsonpath):
                return False, '无法在{}中找到{}'.format(value_by_jsonpath, expectation)
        else:
            logger.error('测试用例中的check_point格式错误，operator == ' + operator)
            return False, '测试用例中的check_point格式错误，operator == ' + operator
    return True, None


def parse_prop_statement(statement: str):
    result = re.match(r'"(.*)"="(.*)"', statement)
    return result.group(1), result.group(2)


def set_props(json_obj, prop_statements: str):
    for statement in prop_statements.split('\n'):
        key, jsonpath = parse_prop_statement(statement)
        logger.info('key={},jsonpath={}'.format(key, jsonpath))
        value = str(get_by_jsonpath(jsonpath, json_obj))
        if isinstance(value, list):
            logger.error("value只能是单个的值，不能是数组！")
            return
        logger.info('value=' + value)
        if props.get(key) is not None:
            logger.warning('props[{}]已经存在，将被覆盖。原值={}，新值={}'.format(key, props[key], value))
        props[key] = value
