import time
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
            
            Best regards.
            
            --
            Yuchen Tian
        """

    def send_as_file(self, receiver, file_content, file_name):
        msg = MIMEMultipart()

        # mail header
        msg['From'] = self.sender
        msg['To'] = receiver
        msg['Subject'] = self.subject

        # mail body
        msg.attach(MIMEText(self.main_text, "plain", "utf-8"))

        # attachment
        attachment = MIMEText(file_content, "base64", "utf-8")
        attachment["Content-Type"] = 'application/octet-stream'
        attachment['Content-Disposition'] = "attachment; filename={0}".format(file_name)
        msg.attach(attachment)

        if not self.reliable_send(receiver, msg):
            print("[email] fail to send report")

    def reliable_send(self, receiver, msg):
        send_num, send_status = 0, False
        while send_num < 3:
            try:
                server = smtplib.SMTP()
                server.connect(self.server)
                server.login(self.sender, self.key)
                server.sendmail(self.sender, receiver, msg.as_string())
                server.quit()
                print("[email] report was sent successfully")
                send_status = True
                break
            except Exception as e:
                print("[email] report-sending error")
                print(e)
                print("[email] trying resending after 1 second...")
                time.sleep(1)
                send_num += 1

        return send_status


sender = Sender()

# test
# sender.send_as_file("tyc896@yeah.net", b'hh', "report.html")
