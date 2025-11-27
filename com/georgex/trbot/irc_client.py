"""
Runnable script for IRC Translation Bot.
"""
import argparse
import sys

from com.georgex.trbot.client_console import ClientConsole
from com.georgex.trbot.irc_server import IrcServer
from com.georgex.trbot.translator import Translator
from com.georgex.trbot.app_config import AppConfiguration

DEFAULT_CONFIG_PATH = 'c:\\Users\\g3org\\PycharmProjects\\IrcTranslationBot\\com\\georgex\\trbot\\config.json'
try:
    parser = argparse.ArgumentParser(description='Configuration for translation bot')
    args = parser.parse_args()
    config_file_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONFIG_PATH
    app_config = AppConfiguration(config_file_path)
    client_console = ClientConsole()
    translator = Translator()
    irc_server = IrcServer(app_config)
    irc_server.register_listener(client_console.on_server_event)
    irc_server.connect()
    while irc_server.connected():
        continue
    sys.exit(0)
except KeyboardInterrupt:
    irc_server.disconnect()
    print('CTRL+C Detected; shutting down')
    sys.exit(0)
except Exception as e:
    print('ERROR:', e)
    irc_server.disconnect()
    sys.exit(-1)