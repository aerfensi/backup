import configparser
from pathlib import Path

Http_ServerCertVerify = False
Http_ServerCert = None
Http_ClientCert = None
Http_Proxy = None
Email_senders = None
Email_recipients = None
report_title = 'None'


def read():
    conf_path = str(Path(__file__).resolve().parents[1] / 'conf.ini')
    print(conf_path)
    config = configparser.ConfigParser()
    config.read(conf_path, encoding='utf-8')

    global Http_ServerCertVerify
    Http_ServerCertVerify = config.getboolean('Http', 'ServerCertVerify')

    global Http_ServerCert
    Http_ServerCert = config['Http']['ServerCert']

    global Http_ClientCert
    Http_ClientCert = config['Http']['ClientCert']

    global Http_Proxy
    Http_Proxy = config['Http']['Proxy']

    global Email_senders
    Email_senders = config['Email']['sender']

    global Email_recipients
    Email_recipients = config['Email']['recipients']

    global report_title
    report_title = config['Default']['ReportTitle']


if __name__ == '__main__':
    read()
    print(globals())
