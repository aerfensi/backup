import configparser
from pathlib import Path
from pprint import pprint
from time import strftime

"""
读取conf.ini中的配置，并设置一些供其他模块读取的全局变量
"""

debug = False

server_cert_verify = False
server_cert = None
client_cert = None
proxy = None

mail_from = None
mail_to = None
mail_cc=None
mail_host=None
mail_port=None
mail_user=None
mail_password=None

report_title = 'None'
timestamp = strftime('%Y-%m-%d_%H-%M-%S')
# test_name会被用在生成的log文件名、测试报告文件名、压缩文件名、发送的邮件标题等等中
test_name=None

prj_path = Path(__file__).resolve().parents[1]
conf_path = prj_path / 'conf.ini'
logs_path = prj_path / 'logs'
tcs_path = prj_path / 'testcases'
res_path = prj_path / 'res'
props_path = prj_path / 'props'
reports_path=prj_path / 'reports'


def read():
    config = configparser.ConfigParser()
    config.read(str(conf_path), encoding='utf-8')

    global server_cert_verify
    server_cert_verify = config.getboolean('Http', 'ServerCertVerify')

    if config['Http']['ServerCert']:
        global server_cert
        server_cert = str(res_path / config['Http']['ServerCert'])

    if config['Http']['ClientCert']:
        global client_cert
        client_cert = str(res_path / config['Http']['ClientCert'])

    global proxy
    proxy = config['Http']['Proxy']

    global mail_from
    mail_from = config['Email']['From']

    global mail_to
    mail_to = config['Email']['To']

    global mail_cc
    mail_cc = config['Email']['Cc']

    global report_title
    report_title = config['Default']['ReportTitle']

    global mail_host
    mail_host=config['Email']['Host']

    global mail_port
    mail_port = config.getint('Email','Port')

    global mail_user
    mail_user = config['Email']['User']

    global mail_password
    mail_password = config['Email']['Password']

    global debug
    debug = config.getboolean('Default', 'Debug')

    global test_name
    test_name = '{}_{}'.format(report_title,timestamp)

read()

if __name__ == '__main__':
    pprint(globals())
