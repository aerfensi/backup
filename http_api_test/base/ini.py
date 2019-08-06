import configparser
from pathlib import Path
from pprint import pprint

# DEBUG开启后，logger的level设置为debug，log输出到屏幕而不是文件，不生成report，测试用例中设置的属性{{}}保存到文件props
DEBUG = True
Http_ServerCertVerify = False
Http_ServerCert = None
Http_ClientCert = None
Http_Proxy = None
Email_senders = None
Email_recipients = None
report_title = 'None'
PRJ_PATH = Path(__file__).resolve().parents[1]
CONF_PATH = PRJ_PATH / 'conf.ini'
LOGS_PATH = PRJ_PATH / 'logs'
TCS_PATH = PRJ_PATH / 'testcases'
RES_PATH = PRJ_PATH / 'res'
PROPS_PATH = PRJ_PATH / 'props'

def read():
    config = configparser.ConfigParser()
    config.read(str(CONF_PATH), encoding='utf-8')

    global Http_ServerCertVerify
    Http_ServerCertVerify = config.getboolean('Http', 'ServerCertVerify')

    global Http_ServerCert
    Http_ServerCert = RES_PATH / config['Http']['ServerCert'] if config['Http']['ServerCert'] else None

    global Http_ClientCert
    Http_ClientCert = RES_PATH / config['Http']['ClientCert'] if config['Http']['ClientCert'] else None

    global Http_Proxy
    Http_Proxy = config['Http']['Proxy']

    global Email_senders
    Email_senders = config['Email']['sender']

    global Email_recipients
    Email_recipients = config['Email']['recipients']

    global report_title
    report_title = config['Default']['ReportTitle']


if __name__ == '__main__':
    pass