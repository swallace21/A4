from mailbot import register, Callback

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import statsmodels.formula.api as smf
import email, time, datetime, pytz, imaplib

# Email settings
imap_server = 'imap.gmail.com'
imap_user = 'swallace21@gmail.com'
imap_password = 'yvpkefaxvrliituv'

importantTitles = ['wife','brother','sister','mother','mom','dad','aunt','uncle','grandmother']
feature_cols = ['DayNum','MinsSinceMidnight','isReply','isFwd','impTitles','Jason','Sandi','brother', 'sister', 'mom']

def getData():
    # read data into a DataFrame
    data = pd.read_csv('_data_final2.csv', index_col=False)
    data['DayNum'] = data.Day.map({'Sun':0, 'Mon':1, 'Tue':2, 'Wed':3, 'Thu':4, 'Fri':5, 'Sat':6}) #convert Day of week
    data = data.loc[data['From'].str.contains('swallace21@gmail.com')==False]
    data = data.loc[data['From'].str.contains('sonic.elements@gmail.com')==False]
    data = data.loc[data['From'].str.contains('shaun_wallace@icerm.brown.edu')==False]
    data = data.loc[data['resTime'] > 0]
    data = data.loc[data['resTime'] < 30000] #remove outliers
    return data

def isInHistory(em):
    data = pd.read_csv('_data_final2.csv', index_col=False)
    data = data.loc[data['From'].str.contains(em)==True]

    if len(data) == 0:
        return 0, 0
    if len(data) != 0:
        maxResp = max(data['resTime'])
        #print "maxResp ", maxResp
        return 1, maxResp

def isInHistorySent(em):
    # read data into a DataFrame
    data = pd.read_csv('_data_gathering/raw-email-sent.tsv', delimiter='\t', index_col=False)
    data = data.loc[data['To'].str.contains(em)==True]
    if len(data) == 0:
        return 0
    if len(data) != 0:
        return 1

def greetingSalutation(em):
    if 'alisonwatson21' in em:
    	return 'Alison', 'Love you'
    if 'ireland10806' in em:
    	return 'Mom', 'Love ya'
    if 'lwallace656' in em:
    	return 'Dad', 'Cheers'
    if 'kebw1144' in em:
    	return 'Kyle', 'Cheers'
    if 'mandyw479' in em:
    	return 'Mandy', 'Love ya'
    if 'lexieu66' in em:
    	return 'Lexi', 'Love ya kiddo'
    if 'Margiebird57' in em:
    	return 'Aunt Margaret', 'Love ya'
    if 'amy.birdwell' in em:
    	return 'Amy', 'Love ya'
    if 'Jason.a.birdwell' in em:
    	return 'Jason', 'Cheers'
    if 'jpittle' in em:
    	return 'Joe', 'Cheers'
    if 'jenmarie823' in em:
    	return 'Jenny', 'Cheers'
    if 'rjwwallace' in em:
    	return 'Uncle Roger', 'Cheers'
    return 'Hello', 'Cheers'

def assignDay(day):
    if day == 'Sun':
        return 0
    if day in 'Mon':
        return 1
    if day == 'Tue':
        return 2
    if day == 'Wed':
        return 3
    if day == 'Thu':
        return 4
    if day == 'Fri':
        return 5
    if day == 'Sat':
        return 6

def sendEmail(emailFrom, emailTo, subject, text, attachment):
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
    server.login(emailFrom, imap_password)
    text = msg.as_string()
    server.sendmail(emailFrom, emailTo, text)
    server.quit()

def saveDraft(text):
    msg = MIMEText(text)
    msg = text
    conn = imaplib.IMAP4_SSL(imap_server, port = 993)
    conn.login(imap_user, imap_password)
    conn.select('[Gmail]/Drafts')
    conn.append("[Gmail]/Drafts",
                '',
                imaplib.Time2Internaldate(time.time()),
                str(email.message_from_string(msg)))

def getPredAll(data, values):
    X = data[feature_cols]
    y = data.resTime

    # follow the usual sklearn pattern: import, instantiate, fit
    lm = LinearRegression()
    lm.fit(X, y)

    #test prediction
    #predict for a new observation
    pred = lm.predict(values)

    return pred[0] #minutes

def getPredEmail(data, values, em):
    data = data.loc[data['From'].str.contains(em)==False]
    X = data[feature_cols]
    y = data.resTime

    # follow the usual sklearn pattern: import, instantiate, fit
    lm = LinearRegression()
    lm.fit(X, y)

    #test prediction
    #predict for a new observation
    pred = lm.predict(values)

    return pred[0] #minutes


class MyCallback(Callback):
    #did not set any rules
    #rules = {'subject': [r'Hello (\w)']}
    #print 'test my callback'

    def trigger(self):
        print self.message['subject']
        emailFrom = self.message['from']
        inHist, maxResp = isInHistory(emailFrom)
        inHistSent = isInHistorySent(emailFrom)

        if inHist == 1 and maxResp == 0:
            u='' #placeholder
            #do nothing, it is in history but never received a response
        else:
            subject = self.message['subject']
            isReply = 0
            if 'Re:' in subject:
                isReply = 1
            isFwd = 0
            if 'Fwd:' in subject:
                isFwd = 1

            msg = self.message['RFC822'] #gets full body message to walk through
            impTitles = 0
            countT = 0
            Jason = 0
            Sandi = 0
            brother = 0
            sister = 0
            mom = 0
            if msg != None:
                if msg.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True)
                    if 'Jason' in body:
                        Jason = body.count('Jason')
                    if 'Sandi' in body:
                        Sandi = body.count('Sandi')
                    if 'mom' in body:
                        mom = body.count('mom')
                    if 'brother' in body:
                        brother = body.count('brother')
                    if 'sister' in body:
                        sister = body.count('sister')
                    for title in importantTitles:
                        if title in body:
                            impTitles += body.count(word)
                        countT += 0

            date_tuple = email.utils.parsedate_tz(self.message['date'])
            dt = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple), pytz.timezone('US/Eastern'))
            hour = dt.strftime('%H')
            minute = dt.strftime('%M')

            DayNum = assignDay(dt.strftime('%a'))
            MinsSinceMidnight = (int(hour)*60) + int(minute)

            values = [DayNum,MinsSinceMidnight,isReply,isFwd,impTitles,Jason,Sandi,brother,sister,mom]
            data = getData()
            prediction = getPredAll(data, values)
            if inHist == 1:
                predictionEmail = getPredEmail(data, values, emailFrom)
                #from jeff on slack
                prediction = (prediction * 0.8) + (predictionEmail * 0.2)
            if prediction < 0:
                prediction = 0

            print 'Prediction = ', prediction


            emailBeg, emailEnd = greetingSalutation(emailFrom)

            sendAutomatedEmail = 0
            ### Send automated response ###
            if inHist != 0 or inHistSent == 1: #only send automated response if I have never recieved an email from them
                sendAutomatedEmail = 1
                subject = 'Re: ' + subject
                hours = prediction/60
                days = hours/24
                text = emailBeg + ' this is an automated response from Shaun\'s email assistant.  He developed it for his class.  '
                text += 'The one cool thing about this assistant is it can predict his response time.  '
                if DayNum == 0 or DayNum == 6:
                    text += 'I see it is the weekend.  Shaun might be a bit slower in responding pleas don\'t hold it against him. \n '

                if prediction == 0 and hour < 7: #1 to 2 hours average response time
                    text += 'Hopefully Shaun should reply in in the next 1-2 hours. Thank you for understanding!'
                elif prediction == 0 and hour < 8: #6 to 8 hours average response time
                    text += 'Hello early bird.  Shaun is current sleeping.  Hopefully Shaun should reply in around ' + str(hour-9) + ' hours. Thank you for understanding!'
                elif (prediction + MinsSinceMidnight) < 1440: #24 hours
                    text += 'Hopefully Shaun should reply in around ' + str(prediction) + ' minutes.  Thank you for understanding!'
                elif (prediction + MinsSinceMidnight) < 4320: #2 - 3 days prediction
                    text += 'He should reply in around ' + str(days) + ' days.  Thank you for understanding!'
                elif (prediction + MinsSinceMidnight) < 10080: #4 - 7 days prediction
                    text += 'He should reply in around ' + str(days) + ' days.  Sorry for the delay he is really busy.  Thank you for understanding!'
                else: #over a week
                    text += 'He should reply sometime in the next week or two.  As an automated robot I am very sorry.  Thank you for understanding!'
                try:
                    sendEmail(imap_user, emailFrom, subject, text, '')
                except Exception as e:
                    print("Exception sendEmail - ERROR: ", str(e))

            ######  Save Draft  ######
            text +=  str(sendAutomatedEmail) + ', ' + str(inHist) + ', ' + str(inHistSent) + ', ' + emailFrom + ', ' + str(prediction) + ' mins. ' + str(hours) + ' hours. ' + str(days) + ' days. '
            text = """
            AUTOMATED DRAFT SAVE DETAILS
            """
            text += 'You got an email from ' + emailFrom + '. \n'
            text += 'Subject' + subject + '. \n'
            text += 'Reported response time: ' + str(prediction) + ' mins. ' + str(hours) + ' hours. ' + str(days) + ' days. \n '
            text += 'Greetings: ' + emailBeg + '\n '
            text += 'Salutations: ' + emailEnd + '\n '
            try:
                saveDraft(text)
            except Exception as e:
                print("Exception sendEmail - ERROR: ", str(e))

register(MyCallback)
