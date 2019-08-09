import json
import re

import jsonpath2

from base import logger, props, ini

"""
检查http response的body是否符合测试用例表格中填写的checkpoint。
这么短的代码要分成多个函数来写的原因是，测试用例中的checkpoint可以随便乱填，容易出现各种错误，把各部分的代码分开，方便将来出问题的时候调试。
"""


def get_by_json_path(json_path: str, json_obj):
    result = [i.current_value for i in jsonpath2.match(json_path, json_obj)]
    return result[0] if len(result) == 1 else result


def parse_check_point(checkpoint: str):
    return re.match('(.*?)([=!><][=~]?)(.*)', checkpoint).groups()


def check(json_obj, checkpoints: str):
    """
    :return: check_result, error_msg
    """
    logger.info('json_obj={}'.format(str(json_obj)))
    for checkpoint in checkpoints.split('\n'):
        if not checkpoint:
            continue
        logger.info('checkpoint={}'.format(checkpoint))
        json_path, operator, expectation = parse_check_point(checkpoint)
        logger.info('json_path={}, operator={}, expectation={}'.format(str(json_path), str(operator), str(expectation)))
        value_by_json_path = get_by_json_path(json_path, json_obj)
        logger.info('value_by_json_path={}'.format(str(value_by_json_path)))

        if type(value_by_json_path) != type(eval(expectation)):
            return False, '{} != {}'.format(str(type(value_by_json_path)), str(type(eval(expectation))))

        if operator == '==':
            if value_by_json_path != eval(expectation):
                return False, '预期：{}，实际：{} != {}'.format(checkpoint,str(value_by_json_path), str(eval(expectation)))
        elif operator == '!=':
            if value_by_json_path == eval(expectation):
                return False, '预期：{}，实际：{} == {}'.format(checkpoint,str(value_by_json_path), str(eval(expectation)))
        elif operator == '<':
            if value_by_json_path >= eval(expectation):
                return False, '预期：{}，实际：{} >= {}'.format(checkpoint,str(value_by_json_path), str(eval(expectation)))
        elif operator == '>':
            if value_by_json_path <= eval(expectation):
                return False, '预期：{}，实际：{} <= {}'.format(checkpoint,str(value_by_json_path), str(eval(expectation)))
        elif operator == '<=':
            if value_by_json_path > eval(expectation):
                return False, '预期：{}，实际：{} > {}'.format(checkpoint,str(value_by_json_path), str(eval(expectation)))
        elif operator == '>=':
            if value_by_json_path < eval(expectation):
                return False, '预期：{}，实际：{} < {}'.format(checkpoint,str(value_by_json_path), str(eval(expectation)))
        elif operator == '=~':
            if not isinstance(value_by_json_path, str):
                return False, '{}不是字符串类型'.format(str(value_by_json_path))
            if not re.search(expectation, value_by_json_path):
                return False, '无法在{}中找到{}'.format(value_by_json_path, expectation)
        else:
            logger.error('测试用例中的check_point格式错误，operator == ' + operator)
            return False, '测试用例中的check_point格式错误，operator == ' + operator
    return True, None


def parse_prop_statement(statement: str):
    return re.match('"(.*?)"="(.*)"', statement).groups()


def set_props(json_obj, prop_statements: str):
    for statement in prop_statements.split('\n'):
        if not statement:
            continue
        key, json_path = parse_prop_statement(statement)
        logger.info('key={},json_path={}'.format(key, json_path))
        value = get_by_json_path(json_path, json_obj)
        logger.info('value=' + str(value))
        if isinstance(value, list):
            logger.error("value只能是单个的值，不能是数组！")
            return
        if props.get(key) is not None:
            logger.warning('props[{}]已经存在，将被覆盖。原值={}，新值={}'.format(key, props[key], str(value)))

        props[key] = str(value)
        if ini.debug:
            with ini.props_path.open(mode='w+', encoding='utf-8') as file:
                json.dump(props,file)
