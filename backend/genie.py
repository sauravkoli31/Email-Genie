import imaplib
import datetime
import time
import pandas as pd
import email
from email.header import decode_header
import dotenv
import sys
import os
import tldextract

dotenv.load_dotenv()
class genie():
    def __init__(self,username,password):
        self.username = username
        self.password = password

    def process(self, data):
        '''
        Extract data from email headers and decode them based on the encoding type
        :param data:
        :return:
        '''
        self.rt = ''
        self.enc = None
        for self.extract, self.encoding in decode_header(self.data):
            if self.encoding is not None:
                self.enc = self.encoding
        for self.extract, self.encoding in decode_header(self.data):
            if self.extract is not None:
                # if it's a bytes, decode to str
                if self.enc == 'unknown-8bit':
                    self.rt = self.rt + self.extract.decode('utf-8')
                elif self.enc == None :
                    self.rt = self.rt + self.extract
                else:
                    self.rt = self.rt + self.extract.decode(self.enc)
        return self.rt


    def check_mailbox(self):
        '''
        Check all the mailboxes in the account
        :param u: Username
        :param p: Password
        :return: return a list with all the mailboxes and number of emails in each mailbox
        '''
        print(f'{"Checking mailbox":^60}')
        self.mailbox_list = []
        self.imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        self.imap.login(self.username, self.password)
        self.rv, self.mailboxes = self.imap.list()
        for self.mb in self.mailboxes:
            self.l = self.mb.decode().split(' "/" ')
            self.status, self.messages = self.imap.select(self.l[-1])
            self.ml = {}
            self.ml['Mailbox'] = self.l[-1]
            self.ml['Count'] = int(self.messages[0]) if self.messages[0].isdigit() else 0
            self.mailbox_list.append(self.ml)
        self.imap.close()
        self.imap.logout()
        return self.mailbox_list


    def fetch_emails(self):
        '''
        FUNCTION TO FETCH ALL EMAILS FROM THE MAILBOX
        :return:
        '''
        self.lst = []
        self.count = 0

        self.imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        self.imap.login(self.username, self.password)
        self.rv, self.mailboxes = imap.list()
        print(self.rv,self.mailboxes)
        self.status, self.messages = self.imap.select()
        # num = [i for i in range(1,11)]
        self.num = [i for i in range(1,int(self.messages[0])+1)]
        self.fetch_ids = ','.join(map(str,self.num))
        print(int(self.messages[0]))
        self.res, self.msg = self.imap.fetch(str.encode(self.fetch_ids), '(RFC822.HEADER BODY.PEEK[1])')
        with open("../data/raw.txt", "a+", encoding="utf-8") as self.f:
            for self.response in self.msg:

                if isinstance(self.response, tuple):
                    self.count+=1
                    sys.stdout.write("\r" + str(self.count))
                    sys.stdout.flush()
                    # parse a bytes email into a message object
                    self.msg = email.message_from_bytes(self.response[1])
                    self.f.write(str(self.msg))
                    self.f.write("\r\n")
                    self.f.write(str(self.count))
                    self.f.write("    ")
                    self.f.write("#"*200)
                    self.f.write("\r\n")
                    # Decode the email subject
                    if self.msg["Subject"] is not None:
                        self.subject_all = self.process(self.msg["Subject"])
                    else:
                        self.subject_all = ''

                    # decode email sender
                    if self.msg.get("From") is not None:
                        self.From = self.process(self.msg.get("From"))
                    else:
                        self.From = ''

                    self.From = self.From.split(" ")[-1]
                    self.From = self.From.replace("<","")
                    self.From = self.From.replace(">","")
                    self.emails = {}
                    if (self.From != ''):
                        self.emails["Subject"] = self.subject_all.replace("\r\n"," ")
                        self.emails["From"] = self.From
                        # print(emails)
                        self.lst.append(self.emails)
        self.f.close()
        self.imap.close()
        self.imap.logout()

        df = pd.DataFrame(self.lst)
        df.to_csv('../data/emails.csv',index=False)

if __name__ == '__main__':
    username = os.getenv("MAIL")
    password = os.getenv("PASSWORD")
    gs = genie(username,password)
    ml = gs.check_mailbox()
    for data in ml:
        print(f'{data["Mailbox"]:<30}{data["Count"]:>10}')
    # mb = check_mailbox(username,password)
    # ln=mb[0]['Count']
    # for i in mb:
    #     if i['Count'] > ln:
    #         ln = i['Count']
    # print(ln)
    # fetch_emails(username,password)
    #
    # df = pd.read_csv('../emails.csv', dtype='unicode')
    # # print(df.describe())
    # # print(df['From'].value_counts())
    # spl = lambda x: x['From'].split("@")[-1]
    # df['Email_domain'] = df.apply(spl, axis=1)
    #
    # sd = lambda x:tldextract.extract(x['Email_domain']).registered_domain
    # df['Root_Domain'] = df.apply(sd,axis=1)
    #
    # domain_count = df['Email_domain'].value_counts()
    # a = pd.DataFrame(domain_count)
    # a.reset_index(inplace=True)
    # a = a.rename(columns={'index':'Domain','Email_domain':'count'})
    # print(a.head(10))