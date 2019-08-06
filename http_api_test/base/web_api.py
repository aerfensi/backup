import json
from pathlib import Path
import requests
import urllib3

from base import ini
from base import logger
import warnings


def key_to_lowercase(d: dict) -> dict:
    """
    将一个dict的key都转换为小写
    """
    r = dict()
    for i in d.items():
        r[i[0].lower()] = i[1]
    return r


def load_multipart(data: list):
    """
    将测试用例表格中读取的body转换为requests需要的files对象
    :param data:
    :return:
    """
    files = {}
    for d in data:
        d = key_to_lowercase(d)
        name = d.get("name")
        file_name = d.get("file_name")
        file_obj = d.get("file_obj")
        content_type = d.get("content-type")
        # f = [name, [file_name, file_object, content-type]]
        f = [None, [None, None, None]]
        if not name:
            continue
        else:
            f[0] = name

        if not file_name and not file_obj:
            continue

        # content-type默认为 text/plain;charset=utf-8
        f[1][2] = content_type if content_type else 'text/plain;charset=utf-8'

        if file_obj and f[1][2].startswith('text/plain'):
            f[1][1] = file_obj

        if file_name and not f[1][2].startswith('text/plain'):
            # 文件名字中不能有斜杠，我一开始还以为这个时随便传的
            warnings.simplefilter('ignore', ResourceWarning)
            f[1][0] = Path(file_name).name
            f[1][1] = ini.RES_PATH.joinpath(file_name).open(mode='rb')

        files[f[0]] = f[1]
    return files


def send_request(testdata):
    method = testdata['method']
    logger.info('method = ' + method)
    url = testdata['url']
    logger.info('url = ' + str(url))
    params = json.loads(testdata['params']) if testdata['params'] else None
    logger.info('params = ' + str(params))
    headers = json.loads(testdata['headers']) if testdata['headers'] else None

    if headers:
        headers = key_to_lowercase(headers)
        content_type = headers.get('content-type')
        if content_type is not None and content_type.startswith('multipart/form-data'):
            files = load_multipart(json.loads(testdata['body'])) if testdata['body'] else None
            # 不要手动添加content-type为multipart/form-data，要让requests自动生成，因为需要requests自动添加boundary
            del headers['content-type']
            body = None
        elif content_type is not None and content_type.startswith('application/x-www-form-urlencoded'):
            files = None
            body = testdata['body'].encode('utf-8')
        else:
            files = None
            body = testdata['body'].encode('utf-8') if testdata['body'] else None
    else:
        files = None
        body = testdata['body'].encode('utf-8') if testdata['body'] else None

    logger.info('headers = ' + str(headers))
    logger.info('body = ' + body.decode('utf-8') if isinstance(body, bytes) else str(body))
    logger.info('files = ' + str(files))

    proxies = json.loads(ini.Http_Proxy) if ini.Http_Proxy else None
    logger.info('proxies = ' + str(proxies))

    if not ini.Http_ServerCertVerify:
        urllib3.disable_warnings()
        verify = False
    elif ini.Http_ServerCertVerify and ini.Http_ServerCert:
        verify = ini.Http_ServerCert
    else:
        verify = True

    if ini.Http_ClientCert:
        cert = ini.Http_ClientCert
    else:
        cert = None

    logger.info('cert = ' + str(cert))
    logger.info('verify = ' + str(verify))

    timeout = int(testdata['timeout']) if testdata['timeout'] else 5

    resp = requests.request(method=method, url=url, params=params, timeout=timeout, headers=headers, data=body,
                            proxies=proxies,
                            verify=verify, cert=cert, files=files)

    return resp
