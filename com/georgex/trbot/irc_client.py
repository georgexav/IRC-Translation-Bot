"""
Runnable script for IRC Translation Bot.
"""
import argparse
import os
import sys
from pathlib import Path

from com.georgex.trbot.app_config import AppConfiguration
from com.georgex.trbot.client_console import ClientConsole
from com.georgex.trbot.irc_server import IrcServer
from com.georgex.trbot.translator import Translator

DEFAULT_CONFIG_FILE='TranslationBotConfig.json'
irc_server = None

def get_config_file():
    #args = parser.parse_args()
    home_directory = Path.home()
    config_file_path = None
    config_file_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(home_directory, DEFAULT_CONFIG_FILE)
    return config_file_path

try:
    parser = argparse.ArgumentParser(description='Configuration for translation bot')
    config_file_path = get_config_file()
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
    print('CTRL+C Detected; shutting down')
    if (irc_server != None):
        irc_server.disconnect()

    sys.exit(0)
except Exception as e:
    print('ERROR:', e)
    if (irc_server != None):
        irc_server.disconnect()
    sys.exit(-1)

