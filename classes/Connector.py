import json
from slack_sdk import WebClient

class Connector:
    def __init__(self):
        #Creds in creds.json file, don't forget to add to .gitignore
        self.creds = self.get_creds()
        self.config = self.get_config()
        self.token = self.creds["raptor_creds"]["token"].strip()
        self.signing_secret = self.creds["raptor_creds"]["signing_secret"].strip()
        self.old_num_artifacts = self.config["old_num_artifacts"]
        self.is_first_run = self.config["is_first_run"]

    def get_creds(self):
        with open('./creds.json') as credentials:
            creds = json.load(credentials)
        return creds
    
    def get_config(self):
        with open('./config.json') as config:
            config = json.load(config)
        return config