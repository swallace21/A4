import imaplib, email, getpass
from email.utils import getaddresses

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
# print(conn.list())
#conn.select("INBOX.Sent Items")
conn.select("INBOX", readonly=True)   # Set readOnly to True so that emails aren't marked as read

# Search for email ids between dates specified
#result, data = conn.uid('search', None, '(SINCE "01-Jan-2016")')
result, data = conn.uid('search', None, '(SINCE "16-Apr-2015")')
# result, data = conn.uid('search', None, '(SINCE "01-Jan-2013" BEFORE "01-Jan-2014")')
# result, data = conn.uid('search', None, '(BEFORE "01-Jan-2014")')
# result, data = conn.uid('search', None, '(TO "user@example.org" SINCE "01-Jan-2014")')

uids = data[0].decode('utf-8').split()
#uids = [i.decode('utf-8') for i in uids]

# Download headers
#result, data = conn.uid('fetch', ','.join(uids), '(BODY[HEADER.FIELDS (MESSAGE-ID FROM TO CC DATE)])')
result, data = conn.uid('fetch', ','.join(uids), '(RFC822)')

# Where data will be stored, Header for TSV file
try:
    raw_file = open('../A4/raw-email-rec.tsv', 'w')
    #raw_file.write("Message-ID\tDate\tFrom\tTo\tCc\tMultiPart\tBody\tBodyMM\t\n")
    raw_file.write("Message-ID\tDate\tFrom\tTo\tCc\tMultiPart\tBody\t\n")
except Exception as e:
    print("Exception raw_file_write: ", str(e))


# Parse data and spit out info
for i in range(0, len(data)):

    # If the current item is _not_ an email header
    if len(data[i]) != 2:
        continue

    # Okay, it's an email header. Parse it.
    msg = email.message_from_string(data[i][1].decode('utf-8'))

    mids = msg.get_all('message-id', None)
    mdates = msg.get_all('date', None)
    senders = msg.get_all('from', [])
    receivers = msg.get_all('to', [])
    ccs = msg.get_all('cc', [])

    msgBytes = email.message_from_bytes(data[i][1])
    body = ''
    bodyMM = ''
    multiPart = 'False'
    if msgBytes.is_multipart():
        bodyMM = msgBytes.get_payload()
    else:
        multiPart = 'True'
        body = msgBytes.get_payload()


    row = "\t" if not mids else mids[0] + "\t"
    row += "\t" if not mdates else mdates[0] + "\t"

    # Only one person sends an email, but just in case
    for name, addr in getaddresses(senders):
        row += addr + " "
    row += "\t"

    # Space-delimited list of those the email was addressed to
    for name, addr in getaddresses(receivers):
        row += addr + " "
    row += "\t"

    # Space-delimited list of those who were CC'd
    for name, addr in getaddresses(ccs):
        row += addr + " "
    row += "\t"

    row += multiPart + "\t"

    row += body + "\t"

    #row += bodyMM + "\t"

    row += "\n"

    # DEBUG
    #print(msg.keys())

    # Just going to output tab-delimited, raw data. Will process later.
    raw_file.write(row)


# Done with file, so close it
raw_file.close()
conn.close()
conn.logout()
