import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

#originally from: http://naelshiab.com/tutorial-send-email-python/
class SendEmail(object):
    def send(emailFrom, emailTo, subject, text, attachment):
        emailFrom = 'swallace21@gmail.com'
        emailTo = 'swallace21@gmail.com'
        subject = "Hello"
        text = "Text you want to send.  Hellow World"

        msg = MIMEMultipart()

        msg['From'] = emailFrom
        msg['To'] = emailTo
        msg['Subject'] = subject

        body = text

        msg.attach(MIMEText(body, 'plain'))

        if attachment != '':
            filename = "NAME OF THE FILE WITH ITS EXTENSION"
            attachment = open("PATH OF THE FILE", "rb")

            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

            msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(emailFrom, "")
        text = msg.as_string()
        server.sendmail(emailFrom, emailTo, text)
        server.quit()
