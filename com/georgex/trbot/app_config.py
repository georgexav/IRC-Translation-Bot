import json

class AppConfiguration:

    def __init__(self, config_file):
        self.config_file = config_file
        with open(self.config_file, 'r') as file:
            self.json_data = json.load(file)
            self.irc_server = self.json_data['server']
            self.port = self.json_data['port']
            self.nickname = self.json_data['nickname']
            self.real_name = self.json_data['real_name']
            self.source_channel = self.json_data['source_channel']
            self.target_channel = self.json_data['target_channel']
            self.target_lang = self.json_data['target_lang']
            self.password = self.json_data['password']

    def get_server(self):
        return self.irc_server

    def get_port(self):
        return self.port

    def get_nickname(self):
        return self.nickname

    def get_real_name(self):
        return self.real_name

    def get_source_channel(self):
        return self.source_channel

    def get_target_channel(self):
        return self.target_channel

    def get_target_language(self):
        return self.target_lang

    def get_password(self):
        return self.password