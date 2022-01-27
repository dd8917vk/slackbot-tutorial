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
from classes.Connector import Connector

class RaptorBot(Connector):
    def __init__(self):
        super().__init__()
        #Inhereted from Connector, create web client with slack token
        self.SLACK_BOT_TOKEN = self.token
        self.SLACK_CLIENT = WebClient(self.SLACK_BOT_TOKEN) 
        self.log_path = os.getcwd()+'/bot.log'
        self.channel = '#general'

    def send_message(self, message):
        #If you get ssl error, go to your python installation directory and run install certs sh (google it)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        sc = WebClient(self.SLACK_BOT_TOKEN,ssl=ssl_context)
        # make the POST request through the python slack client
        try:
            self.SLACK_CLIENT.chat_postMessage(
            channel=self.channel,
            text=message
            )#.get()
        #if there is an error, append it to the log
        except SlackApiError as e:
            if not os.path.isfile(self.log_path):
                #create logging file if it doesn't exist
                with open(log_path, 'a') as file:
                    pass
            #log error if slack message doesn't go through
            logging.basicConfig(filename=self.log_path, level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s') 
            logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
            return logging.error(e.response)

    def scrape(self):
        session = HTMLSession()
        req = session.get('https://docs.velociraptor.app/exchange/')
        #Have to call html render to force javascript to load so html can be scraped
        req.html.render()
        html = req.html.find('div.row')
        #This is the number of div's each containing one artifact on the web page
        current_num_artifacts = len(html[1].find('a.title'))
        #This is the top artifact on the page
        top_artifact = html[1].find('a.title')[0]
        #A link to the top (new or latest) artifact on the page for slack message
        link_to_artifact = f"https://docs.velociraptor.app/{list(top_artifact.links)[0]}"
        # return (current_num_artifacts, link_to_artifact)
        return self.check_new_artifact(current_num_artifacts, link_to_artifact)

    def check_new_artifact(self, current_num_artifacts, link_to_artifact):
        print(f'Current num artifacts from raptor: {current_num_artifacts}')
        prev_count = os.getcwd()+'/prev_count.txt'
        try:
        #try reading previous count artifacts from static text file to compare to new num from exchange
            with open(prev_count, 'r') as file:
                old_count = int(file.readlines()[0])
                print(f'Old count artifacts from text file: {old_count}')
                if old_count < current_num_artifacts:
                    print('counts are different, do something')
                    self.send_message("```Standby for a new artifact...```")
                    time.sleep(1)
                    self.pureimg()
        #if file with num_artifacts doesn't exist, create it and write the num_artifacts
        except FileNotFoundError:
            with open(prev_count, 'w') as file:
                file.writelines(str(current_num_artifacts))
        if not os.path.isfile(prev_count):
            with open(prev_count, 'w') as file:
                file.writelines(str(current_num_artifacts))

    def pureimg(self):
        try:
            response = self.SLACK_CLIENT.files_upload(file='./gifs/clever.gif', channels=self.channel)
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            logging.basicConfig(filename=self.log_path, level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s') 
            logging.error('Request to Slack API Failed: {}.'.format(e.response.status_code))
            logging.error(e.response)



            # assert e.response["ok"] is False
            # assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            # print(f"Got an error: {e.response['error']}")

    # def pureimg(self):
    #     def subimg(data):
    #         data = '[{"text": "", "image_url": "'+data+'"}]'
    #         data = [json.loads(data[1:-1])]
    #         return data

    #     slacker = WebClient(token=self.token)
    #     #This function will make the image url to correct format.
    #     clever = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'clever.png')
    #     print(clever)
    #     response = slacker.files_upload(channel='#general',file=clever)
    #     clever = response['file']['permalink']

    #     #It gives cross OS compatibility on filepath.
    #     slacker.chat_postMessage(channel='general', text="Sample Text", username='testbot', attachments=subimg(clever), icon_emoji=':lizard:')


        # print(current_num_artifacts)
        # print(html)

    # b.send_message("hello")
    # messages = ["hello", "thomas", "nichols", "I am a bot from james' imagination"]
    # for m in messages:
    #     b.send_message(m)
    #     time.sleep(1)
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