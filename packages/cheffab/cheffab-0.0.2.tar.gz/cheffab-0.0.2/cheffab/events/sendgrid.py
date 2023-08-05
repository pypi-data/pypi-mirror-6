import socket
import logging
import smtplib

from email.mime.text import MIMEText


from cheffab.events.base import BaseChefFabEvent


class SendGridEvent(BaseChefFabEvent):
    def __init__(self,username,password,recipient):
        self.username = username
        self.password = password
        self.recipient = recipient

    def post(self,event_payload):            
        message_str = "\n".join(["%s: %s" % (key,value) for key,value in event_payload.items()])
        subject_str = "ChefFab Email Alert"
        from_str = "noreply@%s" % socket.gethostname()

        msg = MIMEText(message_str)
        msg['Subject'] = subject_str
        msg['From'] = from_str
        msg['To'] = recipient

        sendmail_options = {
            "from_addr":from_str
            "to_addrs":recipient,
            "msg":msg.as_string()
        }

        try:
            s = smtplib.SMTP(host='smtp.sendgrid.net',port=587)            
            s.login(self.username,self.password)
            s.sendmail(**sendmail_options)
            s.quit()

        except smtplib.SMTPException:
            logging.error("Failed to send email event for %s" % event_payload.get('what',"Unknown Event"))
