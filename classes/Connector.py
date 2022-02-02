import json
from slack_sdk import WebClient

class Connector:
    def __init__(self):
        #Creds in creds.json file, don't forget to add to .gitignore
        self.creds = self.get_creds()
        self.config = self.get_config()
        self.slack_token = self.creds["raptor_creds"]["slack_token"].strip()
        self.slack_signing_secret = self.creds["raptor_creds"]["slack_signing_secret"].strip()
        self.slack_webhook_url = self.creds["raptor_creds"]["slack_webhook_url"]

    def get_creds(self):
        with open('./creds.json') as credentials:
            creds = json.load(credentials)
        return creds
    
    def get_config(self):
        with open('./config.json') as config:
            config = json.load(config)
        return config