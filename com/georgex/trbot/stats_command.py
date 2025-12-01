from datetime import datetime

from client_stats import ClientStats
from abstract_bot_command import AbstractBotCommand
from util import Util


class StatsCommand(AbstractBotCommand):

    def __init__(self, message):
        super().__init__(message)
        self.date_formatter = '%Y-%m-%d %H:%M:%S %Z'

    def execute(self):
        responses = []
        nick = self.app_config.get_nickname()
        start_time = ClientStats.start_time
        start_time_fmt = start_time.strftime(self.date_formatter)
        now = datetime.now()
        time_difference = now.astimezone() - start_time
        duration = Util.time_diff_as_hhmmss(self, time_difference)
        responses.append(f'{nick} has been running since {start_time_fmt}')
        responses.append(f'Session duration: {duration}')
        responses.append(f'{ClientStats.ping_count} PINGS received and processed from server.')
        responses.append(f'{ClientStats.message_count} messages processed for translation.')
        return responses