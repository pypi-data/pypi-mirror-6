#!/usr/bin/env python
import smtplib, logging as log 
from email.mime.text import MIMEText
import pdb

def send_mail(server,sender,recipients,message,subject="",password="",port=587):
    # pdb.set_trace()
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    msg = MIMEText(message)
    msg.add_header('Subject', subject)
    msg.add_header('From', sender)
    msg.add_header('MIME-Version', "1.0")
    msg.add_header('Content-Type', "text/html")
    for recipient in recipients:
        msg.add_header('To', recipient)
    session = smtplib.SMTP(server, port)
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(sender, password)
    to = msg.get_all("To")
    session.sendmail(sender, to, msg.as_string())
    session.quit()

def _test():
    log.debug("test message")
    server = "smtp.gmail.com"
    port = 587
    sender = "shared.house.spicevan@gmail.com"
    password = "gumnuts8"
    subject = "hi"
    message = "hello world"

    # this can be a comma separated list
    # of emails as one long string
    recipients = ["shared.housing.spicevan@gmail.com","fenton.travers@gmail.com"]

    send_mail(server, sender, recipients, message, subject, password, port)
    
if __name__ == '__main__':
    _test()
