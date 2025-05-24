import logging
import email.header
import imaplib
import pandas as pd
import json
from datetime import datetime
from utils.json_files import read_credentials

def decode_mime_words(s):
    return u''.join(
        word.decode(encoding or 'utf8') if isinstance(word, bytes) else word
        for word, encoding in email.header.decode_header(s))

def load_credentials(filepath):
    try:
        user, password = read_credentials(filepath)
        return user, password
    except Exception as e:
        logging.error("Failed to load credentials: {}".format(e))
        raise

def connect_to_gmail_imap(filepath):
    user, password = load_credentials(filepath)
    imap_url = 'imap.gmail.com'
    try:
        mail = imaplib.IMAP4_SSL(imap_url)
        mail.login(user, password)
        mail.select('Inbox')  # Connect to the inbox.
        return mail
    except Exception as e:
        logging.error("Connection failed: {}".format(e))
        raise

def get_emails_from_uber(mail, since, filepath):
    with open(filepath, 'r') as file:
        data = json.load(file)
        emails_from_uber = data['emails']

    email_data = pd.DataFrame(columns=['e-mail', 'count', 'ids'])
    date_filter = (datetime.strptime(since, '%d/%m/%Y %H:%M')).astimezone()
    internal_date = imaplib.Time2Internaldate(date_filter)
    for email in emails_from_uber:
        print(f'Getting emails for the address {email}')
        criteria = 'FROM "{}" SINCE {}"'.format(email, internal_date.split()[0])
        #print(criteria)
        _, messages = mail.search(None, criteria)
        uids = [int(s) for s in messages[0].split()]
        df_dictionary = pd.DataFrame([{'e-mail': email, 'count': len(uids), 'ids': uids}])
        email_data = pd.concat([email_data, df_dictionary], ignore_index=True)
    return email_data