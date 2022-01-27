import json
from slack_sdk import WebClient

class Connector:
    def __init__(self):
        #Creds in creds.json file, don't forget to add to .gitignore
        self.creds = self.get_creds()
        self.token = self.creds["raptor_creds"]["token"].strip()
        self.signing_secret = self.creds["raptor_creds"]["signing_secret"].strip()

    def get_creds(self):
        with open('./creds.json') as credentials:
            creds = json.load(credentials)
        return creds