from com.georgex.trbot.command.AboutCommand import AboutCommand
from com.georgex.trbot.command.StatsCommand import StatsCommand

class BotCommandFactory:

    def __init__(self):
        self.app_config = None
        self.bot_command_indicator = None
        self.bot_command = None

    def set_app_config(self, app_config):
        self.app_config = app_config

    def getCommand(self, chat_message):
        self.chat_message = chat_message
        self.message_text = chat_message.get_chat_message()
        self.tokens = self.message_text.split(' ')
        if (len(self.tokens) < 2):
            raise Exception(f'{self.tokens[0]}: no command specified')
        self.bot_command_indicator = self.tokens[1]
        self.bot_command = self.tokens[1]
        if (self.bot_command_indicator.lower()  == 'about'):
            return AboutCommand(chat_message)
        if (self.bot_command_indicator.lower()  == 'stats'):
            return StatsCommand(chat_message)
        return None