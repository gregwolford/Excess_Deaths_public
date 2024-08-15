# Module for grabbing configurations for the TD Ameritrade API

import configparser

class Configuration:    
    
    def __init__(self, filename='config.txt'):
        self.configParser= configparser.RawConfigParser()
        self.configFilePath=filename
        self.configParser.read(self.configFilePath)
        
        self.username = self.configParser.get('Default', 'username')
        self.api_key = self.configParser.get('Default', 'API_key')