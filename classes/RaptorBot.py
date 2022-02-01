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
                    "raptor_bot":{
                        "is_first_run":False,
                        "old_num_artifacts": current_num_artifacts
                    }
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
                json_string = {
                    "raptor_bot":{
                        "is_first_run":False,
                        "old_num_artifacts": current_num_artifacts
                    }
                }
                
                with open('./config.json', 'w') as outfile:
                    json.dump(json_string, outfile)
                #Continue with the logic of posting the newest artifacts if not first run of program
                if self.old_num_artifacts < current_num_artifacts:
                    print(f'Old num artifacts: {self.old_num_artifacts}')
                    print(f'link length: {len(current_artifact_links)}')
                    new_num_artifacts = current_num_artifacts - self.old_num_artifacts
                    new_links = current_artifact_links[0:new_num_artifacts]
                    self.send_message("```There are new artifacts on the exchange...```")
                    self.send_message("```STAND BY...```")
                    self.attach_image()
                    for link in new_links:
                        self.send_message(f"https://docs.velociraptor.app{link}")
                        time.sleep(0.5)
                #Set old_num_artifacts to current_num_artifacts so program will not run in infinite loop.  old_num_artifacts needs to be updated to current count so when scrape() is called again from the main bot_runner.py file, it will not run the logic send a new slack message again.qqqqtop
                self.old_num_artifacts = current_num_artifacts
                return new_links

        except Exception as e:
            return e 



#     while True:
#         schedule.run_pending()
#         time.sleep(5) # sleep for 5 seconds between checks on the scheduler 