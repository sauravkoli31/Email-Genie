import imaplib
import datetime
import time
import pandas as pd
import email
from email.header import decode_header
import dotenv
import sys
import os
import whois
import tldextract
import matplotlib.pyplot as plt


dotenv.load_dotenv()

def process(data):
    '''
    Extract data from email headers and decode them based on the encoding type
    :param data:
    :return:
    '''
    rt = ''
    enc = None
    for extract, encoding in decode_header(data):
        if encoding is not None:
            enc = encoding
    for extract, encoding in decode_header(data):
        if extract is not None:
            # if it's a bytes, decode to str
            if enc == 'unknown-8bit':
                rt = rt + extract.decode('utf-8')
            elif enc == None :
                rt = rt + extract
            else:
                rt = rt + extract.decode(enc)
    return rt


def check_mailbox(u,p):
    '''
    Check all the mailboxes in the account
    :param u: Username
    :param p: Password
    :return: return a list with all the mailboxes and number of emails in each mailbox
    '''
    username = u
    password = p
    mailbox_list = []
    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    imap.login(username, password)
    rv, mailboxes = imap.list()
    for mb in mailboxes:
        l = mb.decode().split(' "/" ')
        status, messages = imap.select(l[-1])
        ml = {}
        ml['Mailbox'] = l[-1]
        ml['Count'] = int(messages[0]) if messages[0].isdigit() else 0
        mailbox_list.append(ml)
    imap.close()
    imap.logout()
    return mailbox_list


def fetch_emails(u,p):
    '''
    FUNCTION TO FETCH ALL EMAILS FROM THE MAILBOX
    :return:
    '''
    username = u
    password = p
    lst = []
    count = 0

    imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    imap.login(username, password)
    rv, mailboxes = imap.list()
    print(rv,mailboxes)
    status, messages = imap.select()
    # num = [i for i in range(1,11)]
    num = [i for i in range(1,int(messages[0])+1)]
    fetch_ids = ','.join(map(str,num))
    print(int(messages[0]))
    res, msg = imap.fetch(str.encode(fetch_ids), '(RFC822.HEADER BODY.PEEK[1])')
    with open("../raw.txt", "a+", encoding="utf-8") as f:
        for response in msg:

            if isinstance(response, tuple):
                count+=1
                sys.stdout.write("\r" + str(count))
                sys.stdout.flush()
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                f.write(str(msg))
                f.write("\r\n")
                f.write(str(count))
                f.write("    ")
                f.write("#"*200)
                f.write("\r\n")
                # Decode the email subject
                if msg["Subject"] is not None:
                    subject_all = process(msg["Subject"])
                else:
                    subject_all = ''

                # decode email sender
                if msg.get("From") is not None:
                    From = process(msg.get("From"))
                else:
                    From = ''

                From = From.split(" ")[-1]
                From = From.replace("<","")
                From = From.replace(">","")
                emails = {}
                if (From != ''):
                    emails["Subject"] = subject_all.replace("\r\n"," ")
                    emails["From"] = From
                    # print(emails)
                    lst.append(emails)
    f.close()
    imap.close()
    imap.logout()


    df = pd.DataFrame(lst)
    df.to_csv('emails.csv',index=False)

if __name__ == '__main__':
    username = os.getenv("MAIL")
    password = os.getenv("PASSWORD")
    # mb = check_mailbox(username,password)
    # ln=mb[0]['Count']
    # for i in mb:
    #     if i['Count'] > ln:
    #         ln = i['Count']
    # print(ln)
    # fetch_emails(username,password)

    df = pd.read_csv('../emails.csv', dtype='unicode')
    # print(df.describe())
    # print(df['From'].value_counts())
    spl = lambda x: x['From'].split("@")[-1]
    df['Email_domain'] = df.apply(spl, axis=1)

    sd = lambda x:tldextract.extract(x['Email_domain']).registered_domain
    df['Root_Domain'] = df.apply(sd,axis=1)

    domain_count = df['Email_domain'].value_counts()
    a = pd.DataFrame(domain_count)
    a.reset_index(inplace=True)
    a = a.rename(columns={'index':'Domain','Email_domain':'count'})
    print(a.head(10))

    b = [i for i in range(0,1200,5)]
    a['count'].plot(kind='hist',bins=b,rwidth=0.8)
    plt.show()

    # df.to_csv('emails_processed.csv',index=False)