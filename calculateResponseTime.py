# imports
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
import numpy as np
import editdistance as ed
import email, time, datetime, pytz, unicodedata

# read data into a DataFrame
emailRec = pd.read_csv('_data_gathering/raw-email-rec.tsv', delimiter='\t', index_col=False)
emailSen = pd.read_csv('_data_gathering/raw-email-sent.tsv', delimiter='\t', index_col=False)

responseTime = []

#headers
hds = ['Index','MessageID','InReplyTo','Date','Day','Hour','Minute','MinsSinceMidnight','Flags','Subject','isReply','isFwd','From','inFrom','To','inTo','inCc','CcCount','inBcc','MultiPart','BodyLen','BodyLenHTML','impNames','impTitles','impWords','WordsTotal','Wallace','Watson','Alison','Kyle','Mandy','Amanda','Mandy','Lexi','Alexa','Sandi','Lawrence','Larry','Roger','Margaret','Amy','Jason','Josh','Jenny','Birdwell','Nanny','wife','brother','sister','mother','mom','dad','aunt','uncle','grandmother','Love','Wedding','Birthday','Child','Family','Professor','Adjunct','Manager','Developer','Salary','Position','Brown','Mazda']
#headers2 = list(emailRec.columns.values)

#emailRecNP = np.genfromtxt('raw-email-rec.tsv', delimiter='\t', skip_header=0)
#emailSenNP = np.genfromtxt('sent.csv', delimiter=',', skip_header=0)

#tests
#print emailRec.shape
#print emailSen.shape
#print 'Rec ', emailRec.iloc[1, hds.index('Index')] #[1, 0] 1 = row, 0 = col


countR = 0
#countS = 0
for idM in emailRec.MessageID:
    countS = 0
    diffM = 0
    for inRep in emailSen.InReplyTo:
        if idM in emailSen.iloc[countS, hds.index('InReplyTo')]:
            four = '-04:00'
            five = '-05:00'
            recDate = emailRec.iloc[countR, hds.index('Date')]
            senDate = emailSen.iloc[countS, hds.index('Date')]
            if four in recDate:
                recDate = recDate.split(four, 1)[0]
            if five in recDate:
                recDate = recDate.split(five, 1)[0]
            if four in senDate:
                senDate = senDate.split(four, 1)[0]
            if five in senDate:
                senDate = senDate.split(five, 1)[0] #catches only 1 instance
            #recDate = emailRec.iloc[countR, hds.index('Date')].split('-05:00', 1)[0]
            #senDate = emailSen.iloc[countS, hds.index('Date')].split('-05:00', 1)[0]
            recDate = datetime.datetime.strptime(recDate, '%Y-%m-%d %H:%M:%S')
            senDate = datetime.datetime.strptime(senDate, '%Y-%m-%d %H:%M:%S')

            d = senDate - recDate
            diffM = abs(d.days * 1440 + d.seconds / 60)
            print countR, ',', diffM
            #emailSen = emailSen.drop([countS]) #drops row from sent emails since it has been found
            break
        countS += 1
    if diffM == 0:
        print countR, ',', diffM
    responseTime.append(diffM)
    countR += 1


countS += 1
countR += 1

#lis = [0]*len(emailRec)
emailRec['resTime'] = responseTime

#write the final data
emailRec.to_csv('_data_final.csv')
