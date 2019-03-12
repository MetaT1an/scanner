import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Sender(object):
    def __init__(self):
        self.server = "smtp.qq.com"
        self.sender = "yuchentianx@qq.com"
        self.key = "gfuwqqqxqlpudegc"
        self.subject = "Scanning report"
        self.main_text = """
            Hi,
            
            You've received this email because your email address was used for registering our Vulnerability Scanning System.
            
            The attachment in this email is a detailed report about your recent scan task(s).
            
            Have a good day!
        """

    def send_as_file(self, receiver, content, file_name):
        msg = MIMEMultipart()

        # mail header
        msg['From'] = self.sender
        msg['To'] = receiver
        msg['Subject'] = self.subject

        # mail body
        msg.attach(MIMEText(self.main_text, "plain", "utf-8"))

        # attachment
        attachment = MIMEText(content, "base64", "utf-8")
        attachment["Content-Type"] = 'application/octet-stream'
        attachment['Content-Disposition'] = "attachment; filename={0}".format(file_name)
        msg.attach(attachment)

        try:
            server = smtplib.SMTP()
            server.connect(self.server)
            server.login(self.sender, self.key)
            server.sendmail(self.sender, receiver, msg.as_string())
            server.quit()
            print("[email] report was sent")
        except Exception as e:
            print("[email] sent error")
            print(e)


sender = Sender()

# test
# sender.send_as_file("tyc896@qq.com", b'hh', "report.html")
