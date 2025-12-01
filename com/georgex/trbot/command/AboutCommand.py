import langcodes

from com.georgex.trbot.command.AbstractBotCommand import AbstractBotCommand

class AboutCommand(AbstractBotCommand):
    def __init__(self, message):
        super().__init__(message)

    def execute(self):
        responses = []
        nick = self.app_config.get_nickname()
        source_channel = self.app_config.get_source_channel() if self.app_config.get_source_channel().startswith('#') else '#' + self.app_config.get_source_channel()
        target_channel = self.app_config.get_target_channel() if self.app_config.get_target_channel().startswith('#') else '#' + self.app_config.get_target_channel()
        lang_code = self.app_config.get_target_language()
        language = langcodes.Language.make(lang_code).display_name()
        responses.append(f'{nick} is a translation bot developed by asi9.')
        responses.append(f'Messages received in {source_channel} are translated to {language} when they are in another language.')
        responses.append(f'Translated messages are sent to {target_channel}.')
        return responses