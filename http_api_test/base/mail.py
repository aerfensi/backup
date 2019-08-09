import os
import smtplib
import zipfile
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from base import ini
from base import logger

"""
以邮件的形式发送测试报告和log
"""

# 生成的邮件附件的路径
archive_path = str(ini.prj_path / (ini.test_name + '.zip'))

def check():
    """
    检查是否需要发送邮件
    """
    if ini.debug:
        return False
    if not ini.mail_from:
        return False
    if not ini.mail_to and not ini.mail_cc:
        return False
    if not ini.mail_host:
        return False
    if not ini.mail_user:
        return False
    if not ini.mail_password:
        return False
    logger.info('可以发送邮件')
    return True

def zip_attachment(files):
    """
    :param files:list of pathlib.Path
    """
    logger.info(str(files))
    logger.info('archive_path: '+archive_path)
    with zipfile.ZipFile(archive_path, 'w') as archive:
        for i in files:
            archive.write(i, arcname=i.name)


def rm_archive():
    if os.path.isfile(archive_path):
        os.remove(archive_path)

def send():
    logger.info('ini.mail_from: '+str(ini.mail_from))
    logger.info('ini.mail_to: '+str(ini.mail_to))
    logger.info('ini.mail_cc: '+str(ini.mail_cc))
    message = MIMEMultipart()
    message['Subject'] = Header("测试报告："+ini.test_name, 'utf-8')
    message['From'] = ini.mail_from
    message['To'] = ini.mail_to
    message['Cc'] = ini.mail_cc

    with open(archive_path, 'rb') as file:
        att=MIMEApplication(file.read(),'zip')
        att.add_header('content-disposition', 'attachment',
                       filename=('utf-8', '', ini.test_name+'.zip'))
    message.attach(att)

    with smtplib.SMTP_SSL(host=ini.mail_host,port=ini.mail_port if ini.mail_port else 465) as smtpObj:
        smtpObj.login(ini.mail_user, ini.mail_password)
        smtpObj.sendmail(ini.mail_from, ini.mail_to.split() + ini.mail_cc.split(), message.as_string())

if __name__ == '__main__':
    pass