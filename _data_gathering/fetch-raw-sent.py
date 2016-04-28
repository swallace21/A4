import imaplib, email, getpass, time, datetime, pytz, unicodedata
from email.utils import getaddresses
from collections import Counter

# Email settings
imap_server = 'imap.gmail.com'
imap_user = 'swallace21@gmail.com'
#imap_password = getpass.getpass()
imap_password = ''

# Connection
conn = imaplib.IMAP4_SSL(imap_server)
(retcode, capabilities) = conn.login(imap_user, imap_password)

#Less Secure Apps
#https://www.google.com/settings/security/lesssecureapps

# Specify email folder
#print(conn.list())
conn.select('"[Gmail]/Sent Mail"')
#conn.select("INBOX", readonly=True)   # Set readOnly to True so that emails aren't marked as read

# Search for email ids between dates specified
#result, data = conn.uid('search', None, '(SINCE "01-Jan-2016")')
result, data = conn.uid('search', None, '(SINCE "1-Apr-2014")')
# result, data = conn.uid('search', None, '(SINCE "01-Jan-2013" BEFORE "01-Jan-2014")')
# result, data = conn.uid('search', None, '(BEFORE "01-Jan-2014")')
# result, data = conn.uid('search', None, '(TO "user@example.org" SINCE "01-Jan-2014")')

uids = data[0].split()

# Download headers
result, data = conn.uid('fetch', ','.join(uids), '(FLAGS RFC822)')

#
headers = "Index\tMessageID\tInReplyTo\tDate\tDay\tHour\tMinute\tMinsSinceMidnight\tFlags\tSubject\tisReply\tisFwd\tFrom\tinFrom\tTo\tinTo\tinCc\tCcCount\tinBcc\tMultiPart\tBodyLen\tBodyLenHTML\timpNames\timpTitles\timpWords\tWordsTotal\t"
importantWords = ['Wallace','Watson','Alison','Kyle','Mandy','Amanda','Mandy','Lexi','Alexa','Sandi','Lawrence','Larry','Roger','Margaret','Amy','Jason','Josh','Jenny','Birdwell','Nanny','wife','brother','sister','mother','mom','dad','aunt','uncle','grandmother','Love','Wedding','Birthday','Child','Family','Professor','Adjunct','Manager','Developer','Salary','Position','Brown','Mazda']
impWordsMatches = [0] * len(importantWords)
for word in importantWords:
    headers += word + '\t'
headers += '\n'
# Where data will be stored, Header for TSV file
try:
    raw_file = open('../A4/raw-email-sent.tsv', 'w')
    raw_file.write(headers)
except Exception as e:
    print("Exception raw_file_write: ", str(e))

# Parse data and spit out info
index = 0
for i in range(0, len(data)):

    # If the current item is _not_ an email header
    if len(data[i]) != 2:
        continue

    # Okay, it's an email header. Parse it.
    msg = email.message_from_string(data[i][1])

    mids = msg.get_all('message-id', None)

    if str(mids) is 'None':
        print 'mids is none'

    inReplyTo = msg.get_all('in-reply-to', None)
    if str(inReplyTo) != 'None':
        inReplyTo = inReplyTo[0]


    mdates = msg.get_all('date', None)
    flags = msg['FLAGS']
    date_tuple = email.utils.parsedate_tz(msg['Date'])

    if date_tuple:
        #convert timezone
        dt = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple), pytz.timezone('US/Eastern'))
        #dateFmt = dt.strftime('%a, %d %b %Y %H:%M:%S %z') #full date information
        day = dt.strftime('%a')
        hour = dt.strftime('%H')
        minute = dt.strftime('%M')
        minsSinceMidnight = (int(hour)*60) + int(minute)
        timestamp = time.mktime(email.utils.parsedate(str(dt.strftime('%a, %d %b %Y %H:%M:%S'))))
        #code to gets difference in mins between dates
        #if flag == 0:
        #    flag = 1
        #    dtTemp = dt
        #d = dtTemp - dt
        #print abs(d.days * 1440 + d.seconds / 60), ' mins'

    subject = msg.get_all('subject', [])

    isReply = 0
    if 'Re:' in subject[0]:
        isReply = 1
    isFwd = 0
    if 'Fwd:' in subject[0]:
        isFwd = 1

    senders = msg.get_all('from', [])
    inFrom = 0
    #conditions = [imap_user, 'sonic.elements@gmail.com', 'shaun_wallace@icerm.brown.edu', 'avaris.studios@gmail.com']
    if (imap_user in senders[0]) or ('sonic.elements@gmail.com' in senders[0]) or ('shaun_wallace@icerm.brown.edu' in senders[0]) or ('avaris.studios@gmail.com' in senders[0]):
        inFrom = 1

    receivers = msg.get_all('to', [])
    inTo = 0
    if imap_user in receivers:
        inTo = 1

    ccs = msg.get_all('cc', [])
    inCC = 0
    countCC = 0
    for cc in ccs:
        ccList = cc.split(',')
        for c in ccList:
            countCC += 1
            if imap_user in c:
                inCC = 1

    bccs = msg.get_all('bcc', [])
    inBCC = 0
    if imap_user in bccs:
        inBCC = 1

    count = 0
    bodyLen = 0
    words = 0
    commonWords = ''
    impWordsMatches = [0] * len(importantWords)
    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True)
            bodyLen = bodyLen + len(body)
            words = words + len(body.split())
            count += 1
            for m in Counter(body.split()).most_common():
                if m[1] > 5 and len(m[0]) > 3:
                    commonWords = ' '.join([m[0], commonWords])
            bodyLen = bodyLen/count
            words = words/count
            cnt = Counter()
            count2 = 0
            for word in importantWords:
                if word in body:
                    impWordsMatches[count2] = body.count(word)
                    #print word, body.count(word)
                count2 += 1

    countHTML = 0
    lenTotHTML = 0
    multiPart = 1
    bodyHTML = msg.get_payload()
    if msg.is_multipart():
        count = 0
        lenTot = 0
        for em in bodyHTML:
            lenTot = len(str(em))
            countHTML = countHTML + 1
        bodyLenHTML = lenTotHTML/countHTML
    else:
        multiPart = 0
        bodyLenHTML = len(bodyHTML)


    #assign rows
    row = str(index) + "\t"

    row += "\t" if not mids else mids[0] + "\t"

    row += str(inReplyTo) + "\t"

    row += str(dt) + "\t"
    row += str(day) + "\t"
    row += str(hour) + "\t"
    row += str(minute) + "\t"
    row += str(minsSinceMidnight) + "\t"

    row += str(flags) + "\t"

    row += str(subject) + "\t"
    row += str(isReply) + "\t"
    row += str(isFwd) + "\t"

    # Only one person sends an email, but just in case
    for name, addr in getaddresses(senders):
        row += addr + " "
    row += "\t"
    row += str(inFrom) + "\t"

    for name, addr in getaddresses(receivers):
        row += addr + " "
    row += "\t"
    row += str(inTo) + "\t"

    row += str(inCC) + "\t"
    row += str(countCC) + "\t"
    row += str(inBCC) + "\t"

    row += str(multiPart) + "\t"

    row += str(bodyLen) + "\t"

    row += str(bodyLenHTML) + "\t"

    countWords = 0
    tot = 0
    wordsTotal = 0
    for word in impWordsMatches:
        tot += word
        wordsTotal += word
        if countWords == 19:
            row += str(tot) + "\t"
            tot = 0
        if countWords == 28:
            row += str(tot) + "\t"
            tot = 0
        if countWords == 41:
            row += str(tot) + "\t"
            tot = 0
        countWords += 1

    row += str(wordsTotal) + "\t"

    for word in impWordsMatches:
        row += str(word) + "\t"

    row += "\n"

    # DEBUG
    #print(msg.keys())

    # Just going to output tab-delimited, raw data. Will process later.
    raw_file.write(row)
    index += 1


# Done with file, so close it
raw_file.close()
conn.close()
conn.logout()
