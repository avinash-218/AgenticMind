import os
import time

from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.search import GmailSearch

class Nodes():
    def __init__(self):
        self.gmail = GmailToolkit()

    def check_email(self, state):
        print("Checking for new emails")
        search = GmailSearch(api_resource=self.gmail.api_resource)
        # emails = search('after:newer_than:1d')  # 1 day old emails
        emails = search('from:sendermail@gmail.com')  # from specific email

        if state['checked_emails_ids']:
            checked_emails = state['checked_emails_ids']
        else:
            checked_emails = []

        thread = [] # email threads
        new_emails = []

        print('Here are the emails:', emails)
        for email in emails:
            # filter unchecked emails, threads, and also sent mails
            if (email['id'] not in checked_emails) and (email['threadId'] not in thread) and os.environ['MY_EMAIL'] not in email['sender']:
                thread.append(email['threadId'])
                new_emails.append({
                    'id': email['id'],
                    'threadId': email['threadId'],
                    'snippet': email['snippet'],
                    'sender': email['sender']
                })

        checked_emails.extend([email['id'] for email in emails])

        return {
            'emails': new_emails,
            'checked_emails_ids': checked_emails
        }

    def wait_next_run(self, state):
        print('Waiting for 10 seconds')
        time.sleep(10)
        return state
    
    def new_emails(self, state):
        if len(state['emails']) ==0:
            print('No new emails')
            return 'end'
        else:
            print('New emails !!!')
            return 'continue'
