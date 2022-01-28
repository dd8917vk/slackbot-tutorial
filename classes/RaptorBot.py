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
import random
from classes.Connector import Connector

class RaptorBot(Connector):
    def __init__(self):
        super().__init__()
        #Inhereted from Connector, create web client with slack token
        self.SLACK_BOT_TOKEN = self.slack_token
        self.SLACK_CLIENT = WebClient(self.SLACK_BOT_TOKEN) 
        self.log_path = os.getcwd()+'/bot.log'
        self.channel = '#general'
        self.old_num_artifacts = self.config["raptor_bot"]["old_num_artifacts"]
        self.is_first_run = self.config["raptor_bot"]["is_first_run"]

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
        current_artifacts = html[1].find('a.title')
        #The number of artifacts currently on the exchange
        current_num_artifacts = len(self.get_artifact_links(current_artifacts))
        current_artifact_links = self.get_artifact_links(current_artifacts)
        #This is the top artifact on the page
        #A link to the top (new or latest) artifact on the page for slack message
        # link_to_artifact = f"https://docs.velociraptor.app/{list(top_artifact.links)[0]}"
        # return (current_num_artifacts, link_to_artifact)
        return self.check_new_artifact(current_num_artifacts, current_artifact_links)

    #Responsible for getting array of links to all artifacts, if more than one artifact is posted we need this
    def get_artifact_links(self, current_artifacts):
        list_artifacts = list(current_artifacts)
        artifact_links = [list(obj.find('a.title')[0].links)[0] for obj in list_artifacts]
        return artifact_links

    def check_new_artifact(self, current_num_artifacts, current_artifact_links):
        config = os.getcwd()+'/config.json'
        try:
        #try reading previous count artifacts from static text file to compare to new num from exchange
            if self.is_first_run:
                json_string = {
                    "is_first_run":False,
                    "old_num_artifacts": current_num_artifacts
                }
                with open('./config.json', 'w') as outfile:
                    json.dump(json_string, outfile)
                #set class variables to current state so on the second run, this will hit the else statement
                self.is_first_run = False
                self.old_num_artifacts = current_num_artifacts
                #call scrape again, to hit the else statement and bypass the first run condition
                #thereby running the rest of the program
                self.scrape()
            else:
                #Continue with the logic of posting the newest artifacts if not first run of program
                if self.old_num_artifacts < current_num_artifacts:
                    print(f'Old num artifacts: {self.old_num_artifacts}')
                    print(f'link length: {len(current_artifact_links)}')
                    new_num_artifacts = current_num_artifacts - self.old_num_artifacts
                    print(current_artifact_links[0:new_num_artifacts])
                    # print(current_artifact_links[:new_num_artifacts])
                    # print(current_artifact_links[:new_num_artifacts])

        except Exception as e:
            return e 


            # with open('./config.json') as file:
            #     current_state = json.load(file)
            #     old_num_artifacts = current_state["num_artifacts"]
            #     is_first_run = current_state["is_first_run"]
            #     if is_first_run
                # old_count = current_state["num_artifacts"]
                # print(old_count)
                # old_count = int(file.readlines()[0])
                # print(f'Old count artifacts from text file: {old_count}')
                # if old_count < current_num_artifacts:
                #     print('counts are different, do something')
                #     self.send_message("```Standby for a new artifact...```")
                #     time.sleep(1)
                #     self.attach_image()
        #if file with num_artifacts doesn't exist, create it and write the num_artifacts

    def attach_image(self):
        random_gif = random.choice(os.listdir(os.getcwd()+'/gifs'))
        try:
            response = self.SLACK_CLIENT.files_upload(file='./gifs/'+random_gif, channels=self.channel)
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