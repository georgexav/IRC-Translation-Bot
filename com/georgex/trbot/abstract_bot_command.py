from abc import ABC, abstractmethod

class AbstractBotCommand(ABC):

    def __init__(self, chat_message):
        self.chat_message = chat_message
        self.message_text = chat_message.get_chat_message()
        self.tokens = self.message_text.split(' ')
        if (len(self.tokens) < 2):
            raise Exception(f'{self.tokens[0]}: no command specified')
        self.bot_command_indicator = self.tokens[0]
        self.bot_command = self.tokens[1]

    @abstractmethod
    def execute(self):
        pass

    def set_app_config(self, app_config):
        self.app_config = app_config