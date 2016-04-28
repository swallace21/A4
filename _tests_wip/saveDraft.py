#http://stackoverflow.com/questions/7519135/creating-a-draft-message-in-gmail-using-the-imaplib-in-python
import imaplib, time, email

# Email settings
imap_server = 'imap.gmail.com'
imap_user = 'swallace21@gmail.com'
imap_password = ''

#body
text = 'save drafts testing drafts'

conn = imaplib.IMAP4_SSL(imap_server, port = 993)
conn.login(imap_user, imap_password)
conn.select('[Gmail]/Drafts')
conn.append("[Gmail]/Drafts",
            '',
            imaplib.Time2Internaldate(time.time()),
            str(email.message_from_string(text)))
