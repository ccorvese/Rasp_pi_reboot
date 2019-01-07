import smtplib # < functionality to send basic emails
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
import mimetypes
from datetime import datetime
import os

creds = open("creds.txt", "r")
creds = creds.readlines()
from_email = creds[0]
password = creds [1]

to_email = open("to_email.txt", "r")
to_email = to_email.readlines()
to_email = to_email[0]


date = datetime.now().strftime("%Y-%m-%d")
log_file_name = "{0}-LOG.txt".format(date)

def find_file_in_dir(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            fileToSend = log_file_name
            ctype, encoding = mimetypes.guess_type(fileToSend)
            if ctype is None or encoding is not None:
                ctype = "application/octet-stream"


            maintype, subtype = ctype.split("/", 1)

            msg = MIMEMultipart()
            msg['From]'] = from_email
            msg['To'] = to_email
            msg['Subject'] = "LOG REPORT FOUND - {0}".format(log_file_name)
            body = """See attached file"""
            msg.attach(MIMEText(body,'plain'))


            fp = open("LOGS/{0}".format(log_file_name), "rb")
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(attachment)
            attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
            msg.attach(attachment)


            mailServer = smtplib.SMTP('smtp.gmail.com', 587)
            mailServer.starttls()
            mailServer.login(from_email, password)
            mailServer.sendmail(from_email, to_email, msg.as_string())
            mailServer.quit()



find_file_in_dir(log_file_name, "LOGS/")


