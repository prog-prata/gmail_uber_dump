#!/usr/bin/env python3

import email
import logging
import argparse

from utils.mailler import connect_to_gmail_imap, get_emails_from_uber
from utils.json_files import read_uber_mail, append, save_file
from utils.uber_mail_parser import get_date_from_message, get_subject_from_message, get_body_from_message, get_total_from_body, get_distance_from_body, get_addresses_from_body

EMAILS_LIST_FILE_NAME = 'mail_lists/uber_list.json'
CREDENTIALS_FILE_NAME = 'config/credentials.json'
DUMPED_FILE_NAME ='data/emails.json'

def get_parameters():
    parser = argparse.ArgumentParser(description="Process named parameters.")
    parser.add_argument("--delete", action="store_true", help="Delete messages dumped from Inbox (boolean, default False)")
    parser.add_argument("--since", required=True, help="Date since the messages are received (string, required), ex.:15/11/2020 00:00")

    args = parser.parse_args()

    return (args.delete, args.since)

def main():
    delete_after, since = get_parameters()
    mail = connect_to_gmail_imap(CREDENTIALS_FILE_NAME)
    emails_df = get_emails_from_uber(mail, since, EMAILS_LIST_FILE_NAME)
    json_data = read_uber_mail(DUMPED_FILE_NAME)
    for index, item in emails_df.iterrows():
        #print(item['e-mail'], item['count'])
        mail_addr = item['e-mail']
        for email_id in item['ids']:
            result, data = mail.fetch(str(email_id), '(RFC822)')
            for response_part in data:
                try:
                    if isinstance(response_part, tuple):
                        message = email.message_from_bytes(response_part[1]) #processing the email here for whatever
                        body = get_body_from_message(message)
                        email_item = {
                            "id": email_id,
                            "email": mail_addr,
                            "subject": get_subject_from_message(message),
                            "date" : get_date_from_message(message),
                            "total": get_total_from_body(body),
                            "distance": get_distance_from_body(body),
                        }
                        addresses = get_addresses_from_body(body) #dictionary format = { addr1: "addr 1", addr2: "addr 2"}
                        email_item.update(addresses)
                        append(json_data, email_item)
                    if delete_after:
                        mail.store(str(email_id), '+FLAGS', '\\Deleted')
                except Exception as e:
                    logging.error("Read e-mail error: {}".format(e))
                
    mail.close()
    save_file(DUMPED_FILE_NAME, json_data)

if __name__ == "__main__":
    main()