from mailbot import MailBot, register

from mycallbacks import MyCallback

import smtplib, sched, time
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

###############################################################################

# Email settings
imap_server = 'imap.gmail.com'
imap_user = 'swallace21@gmail.com'
imap_password = ''

mailbot = MailBot(imap_server, imap_user, imap_password, ssl=True)

def send(emailFrom, emailTo, subject, text, attachment):
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
    server.login(emailFrom, "yvpkefaxvrliituv")
    text = msg.as_string()
    server.sendmail(emailFrom, emailTo, text)
    server.quit()

#register your callback
#register(MyCallback)

#send(imap_user, 'swallace21@gmail.com', 'Hello', 'Testing', '')

# check the unprocessed messages and trigger the callback
mailbot.process_messages()


s = sched.scheduler(time.time, time.sleep)
def runMailbot(sc):
    print "Automated Process Messages..."
    mailbot.process_messages()
    sc.enter(1200, 1, runMailbot, (sc,))

s.enter(1200, 1, runMailbot, (s,)) #every 20 minutes
s.run()
