#!/usr/bin/env python
import smtplib, logging as log 

def send_mail(server,sender,recipient,message,subject="",password="",port=587):
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    headers = ["From: " + sender,
               "Subject: " + subject,
               "To: " + recipient,
               "MIME-Version: 1.0",
               "Content-Type: text/html"]
    headers = "\r\n".join(headers)
    session = smtplib.SMTP(server, port)
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(sender, password)
    session.sendmail(sender, recipient, headers + "\r\n\r\n" + message)
    session.quit()

def _test():
    log.debug("test message")
    server = "smtp.gmail.com"
    port = 587
    sender = "shared.house.spicevan@gmail.com"
    password = "gumnuts8"

    recipient = "fenton.travers@gmail.com"
    subject = "hi"
    message = "hello world"
    send_mail(server, sender, recipient, message, subject, password, port)
    
if __name__ == '__main__':
    _test()
