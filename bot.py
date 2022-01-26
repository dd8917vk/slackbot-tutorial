import json
import os
import schedule
import time
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import ssl
from bs4 import BeautifulSoup
import requests

from requests_html import HTMLSession

class Connector:
    def __init__(self):
        self.creds = self.get_creds()
        self.token = self.creds["token"].strip()
        self.signing_secret = self.creds["signing_secret"].strip()

    def get_creds(self):
        with open('./creds.json') as credentials:
            creds = json.load(credentials)
        return creds


class Bot(Connector):
    def __init__(self):
        super().__init__()
        #Inhereted from Connector
        self.SLACK_BOT_TOKEN = self.token
        self.SLACK_CLIENT = WebClient(self.SLACK_BOT_TOKEN) 

    def send_message(self, message):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        sc = WebClient(self.SLACK_BOT_TOKEN,ssl=ssl_context)
    # make the POST request through the python slack client
    # check if the request was a success
        try:
            self.SLACK_CLIENT.chat_postMessage(
            channel='#general',
            text=message
            )#.get()
        except SlackApiError as e:
            log_path = os.getcwd()+'/bot.log'
            if not os.path.isfile(log_path):
                with open(log_path, 'a') as file:
                    pass
            # with open(os.path.join(log_path, 'bot.log'), 'w') as f:
            #     f.write('hello')
            logging.basicConfig(filename=log_path, level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s') 
            logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
            logging.error(e.response)

    def scrape(self):
        # page = requests.get("https://docs.velociraptor.app/exchange/")
        # soup = BeautifulSoup(page.content, 'html.parser')
        session = HTMLSession()
        r = session.get('https://docs.velociraptor.app/exchange/')
        r.html.render()
        x = r.html.find('div.row')
        print(len(x[1].find('a.title')))
        print(x)

if __name__ == "__main__":
    b = Bot()
    b.send_message("hello")
    # print(b.scrape())
    # messages = ["hello", "This is 2", "This is from a loop"]
    # for m in messages:
    #     b.send_message(m)
    #     time.sleep(1)
#     SLACK_BOT_TOKEN = Connector().token
#     slack_client = WebClient(SLACK_BOT_TOKEN)
#     logging.debug("authorized slack client")

#   # # For testing
#     msg = "Good Morning!"
#     send_message(slack_client, msg)
#     schedule.every(60).seconds.do(lambda: send_message(slack_client, msg))

  # schedule.every().monday.at("13:15").do(lambda: sendMessage(slack_client, msg))
    # logging.info("entering loop")

#     while True:
#         schedule.run_pending()
#         time.sleep(5) # sleep for 5 seconds between checks on the scheduler 