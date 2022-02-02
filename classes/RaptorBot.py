import json
import os
import schedule
import time
import logging
from slack_sdk import WebClient
from slack_sdk.webhook import WebhookClient
from slack_sdk.errors import SlackApiError
import ssl
from bs4 import BeautifulSoup
import requests
from requests_html import HTMLSession
import random
from classes.Connector import Connector

random_gifs = ['https://media.giphy.com/media/37Fsl1eFxbhtu/giphy.gif', 'https://media.giphy.com/media/cjJYjxRLgOmEQJ9RVt/giphy.gif', 'https://media.giphy.com/media/3oEjI7REP1DB4KHJDi/giphy.gif', 'https://media.giphy.com/media/3oD3YQjT2cSZTsy6Va/giphy.gif', 'https://media.giphy.com/media/IEkkhUSoBfbPy/giphy.gif', 'https://media.giphy.com/media/q3UEQuCN32ucw/giphy.gif', 'https://media.giphy.com/media/mEi953aP10EgnPKHlZ/giphy.gif', 'https://media.giphy.com/media/m7R82ZvFaEi0U/giphy.gif', 'https://media.giphy.com/media/Up0NsMRidfOso/giphy.gif', 'https://media.giphy.com/media/Wb8ZTJLWJHzkA/giphy.gif', 'https://media.giphy.com/media/KZpZuthdOWQNIzX5mN/giphy.gif', 'https://media.giphy.com/media/GAXMzzd2XElnG/giphy.gif', 'https://media.giphy.com/media/f7BJabcSZhMQMfNh6j/giphy.gif', 'https://media.giphy.com/media/Vd3EREijN5jcXPF6aB/giphy.gif', 'https://media.giphy.com/media/VFe3omOnNcvz9EYeCI/giphy.gif', 'https://media.giphy.com/media/YPPWHPOT4TYZO77bmN/giphy.gif', 'https://media.giphy.com/media/dz6Oy9BQUjlVYezwFo/giphy.gif', 'https://media.giphy.com/media/YTQTRo8zRB2vzDrnSI/giphy.gif', 'https://media.giphy.com/media/M9TraSZZ6csmhxyxRo/giphy.gif']

class RaptorBot(Connector):
    def __init__(self):
        super().__init__()
        #Inhereted from Connector, create web client with slack token
        self.SLACK_BOT_TOKEN = self.slack_token
        self.SLACK_CLIENT = WebhookClient(self.slack_webhook_url) 
        # self.SLACK_CLIENT = WebClient(self.SLACK_BOT_TOKEN) 
        self.log_path = os.getcwd()+'/bot.log'
        self.channel = '#general'
        self.old_num_artifacts = self.config["raptor_bot"]["old_num_artifacts"]
        self.is_first_run = self.config["raptor_bot"]["is_first_run"]

    def send_message(self, gif, link):
        print('from send_message')
        try:
            self.SLACK_CLIENT.send(
                text="test",
                blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "A new Raptor artifact has been released!"
                    }
                },
                {
                    "type": "section",
                    "block_id": "section567",
                    "text": {
                        "type": "mrkdwn",
                        "text": f":t-rex: <https://docs.velociraptor.app{link}|Take me to the Artifact!>  :t-rex: \n Or visit the exchange, \n https://docs.velociraptor.app/exchange/"
                    },
                    "accessory": {
                        "type": "image",
                        "image_url": gif,
                        "alt_text": "Raptor Image Failed to Load."
                    }
                }
            ]
            )
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
                    for link in new_links:
                        self.send_message(random.choice(random_gifs), link)
                        time.sleep(1)
                #Set old_num_artifacts to current_num_artifacts so program will not run in infinite loop.  old_num_artifacts needs to be updated to current count so when scrape() is called again from the main bot_runner.py file, it will not run the logic send a new slack message again.qqqqtop
                self.old_num_artifacts = current_num_artifacts
                return new_links

        except Exception as e:
            return e 

