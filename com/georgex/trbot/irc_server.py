import socket
import ssl
import sys
import threading
import time
import traceback
from datetime import datetime

from com.georgex.trbot.chat_message import ChatMessage
from com.georgex.trbot.irc_command import IrcCommand
from com.georgex.trbot.server_event import ServerEvent
from com.georgex.trbot.server_message import ServerMessage
from com.georgex.trbot.translator import Translator
from com.georgex.trbot.command.bot_command_factory import BotCommandFactory

class IrcServer:
    """
        Handles client communication with IRC server.
    """

    def __init__(self, app_config):
        """
        Constructor
        :param app_config: the JSON file containing application configuration options
        """
        self.app_config = app_config
        self.irc_server = app_config.get_server()
        self.irc_port = int(app_config.get_port(), base=10)
        self.nickname = app_config.get_nickname()
        self.source_channel = app_config.get_source_channel()
        self.target_channel = app_config.get_target_channel()
        self.target_lang = app_config.get_target_language()
        self.real_name = app_config.get_real_name()
        self.password = app_config.get_password()
        self.is_connected = False
        self.message_thread = None
        self.received_message_count = 0;
        self.set_message_count = 0;
        self.listener_list = []
        self.ping_count = 0
        self.start_time = None
        self.last_pong_time = None
        self.irc_command = None
        self.translator = Translator()

    def connect(self):
        """ Connect to IRC server """
        self.irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_context = ssl.create_default_context()
        self.secure_socket = ssl_context.wrap_socket(self.irc_socket, server_hostname=self.irc_server)
        self.message_stream = self.secure_socket.makefile('r')
        self.secure_socket.connect((self.irc_server, self.irc_port))
        self.start_time = datetime.now()
        self.last_pong_time = self.start_time
        self.secure_socket.send(f"USER {self.nickname} 0 * :{self.real_name}\r\n".encode('utf-8'))
        self.secure_socket.send(f"NICK {self.nickname}\r\n".encode('utf-8'))
        self.secure_socket.send(f"IDENTIFY {self.password}\r\n".encode('utf-8'))
        self.is_connected = True
        self.message_thread = threading.Thread(target=self.process_message, daemon=True)
        self.message_thread.start()
        time.sleep(2)
        self.irc_command = IrcCommand(self.secure_socket)
        join_command = self.irc_command.get_join_command(self.source_channel)
        self.fire_server_event(ServerEvent(ServerEvent.OUTGOING_MESSAGE_EVENT, join_command))
        self.irc_command.join_channel(self.source_channel)
        join_command = self.irc_command.get_join_command(self.target_channel)
        self.fire_server_event(ServerEvent(ServerEvent.OUTGOING_MESSAGE_EVENT,join_command))
        self.irc_command.join_channel(self.target_channel)

    def process_message(self):
        """ Process messages received from IRC server """
        while self.is_connected:
            try:
                for message in self.message_stream:
                    self.server_message = ServerMessage(message.strip())
                    message_event = ServerEvent(ServerEvent.INCOMING_MESSAGE_EVENT, self.server_message)
                    self.fire_server_event(message_event)
                    if (self.server_message.is_ping()):                 # logic to response to server PING
                        pong_token = f"{message[6:].strip()}"
                        self.onPing(pong_token)
                        continue
                    if (self.server_message.is_privmsg()):
                        self.onChatMessage(message.strip())
                        continue
            except ssl.SSLError as e:
                print(f"SSL Error: {e}")
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
                self.is_connected = False
                break
            except Exception as e:
                print(f"Error: {e}")
                traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)
                self.is_connected = False
                break

    def onPing(self, token):
        """
        PING message handler.
        :param token: the token to be used for the PONG response
        :return: the PONG response sent to the server
        """
        pong_command = self.irc_command.pong(token)
        self.ping_count += 1
        self.fire_server_event(ServerEvent(ServerEvent.OUTGOING_MESSAGE_EVENT, pong_command))
        return pong_command

    def onChatMessage(self, message):
        """
        PRIVMSG message handler.
        :param message: the PRIVMSG message received from the IRC server
        :return: the translated PRIVMSG message sent to the server
        """
        chat_message = ChatMessage(message)
        condition_a = self.is_source_channel(chat_message.get_channel())
        condition_b = self.is_target_channel(chat_message.get_channel())
        if (not (condition_a or condition_b) ):
            return
        if (chat_message.is_bot_command(self.nickname)):
            self.onBotCommand(chat_message)
            return
        sender_nick = chat_message.get_sender_nick()
        try:
            detected_lang = self.translator.get_language_code(chat_message.get_chat_message())
        except Exception as ex:
            translated_message = chat_message.get_chat_message() + " (Failed to detect language; cause: " + str(ex) + ")"
            self.send_to_xlate_channel(sender_nick, translated_message)
            return translated_message
        #print('Detected lang ' + detected_lang)
        translated_message = None
        if (detected_lang == self.target_lang):
            translated_message = chat_message.get_chat_message() # no translation required
            self.send_to_xlate_channel(sender_nick, translated_message)
            return;
        lang = self.translator.get_language(detected_lang)
        try:
            translated_message = self.translator.translate(chat_message.get_chat_message(), detected_lang, self.target_lang)
        except Exception as ex:
            translated_message = chat_message.get_chat_message() +  " (Failed to translate language; cause: " + str(ex) + ")"
            self.send_to_xlate_channel(sender_nick, translated_message)
            return translated_message

        translated_message = translated_message + " (translated from " + lang.display_name() + ")"
        self.send_to_xlate_channel(sender_nick, translated_message)
        return translated_message

    def onBotCommand(self, chat_message):
        bot_command = BotCommandFactory().getCommand(chat_message)
        bot_command.set_app_config(self.app_config)
        responses = bot_command.execute()
        for response in responses:
            chat_command = self.irc_command.chat_message(self.nickname, chat_message.get_channel(), response)
            self.fire_server_event(ServerEvent(ServerEvent.OUTGOING_MESSAGE_EVENT, chat_command))

    def send_to_xlate_channel(self, nick, message):
        message_to_send = nick + " says: " + message
        chat_command = self.irc_command.chat_message(self.nickname, self.target_channel, message_to_send)
        self.fire_server_event(ServerEvent(ServerEvent.OUTGOING_MESSAGE_EVENT, chat_command))

    def is_source_channel(self, channel):
        source_channel = self.app_config.get_source_channel() if self.app_config.get_source_channel().startswith("#") else "#" + self.app_config.get_source_channel()
        current_channel = channel if channel.startswith("#") else "#" + channel()
        return current_channel == source_channel

    def is_target_channel(self, channel):
        target_channel = self.app_config.get_target_channel() if self.app_config.get_target_channel().startswith("#") else "#" + self.app_config.get_target_channel()
        current_channel = channel if channel.startswith("#") else "#" + channel()
        return current_channel == target_channel

    def disconnect(self):
        """ Disconnect from IRC server """
        #self.show_message('isConnected set to False')
        self.is_connected = False
        self.irc_socket.close();
        #self.message_thread.join()

    def connected(self):
        return self.is_connected

    def register_listener(self, server_event_listener):
        """
        Register a server event listener.
        :param server_event_listener: the listener to be registered
        :return: None
        """
        self.listener_list.append(server_event_listener)

    def fire_server_event(self, server_event):
        for listener in self.listener_list:
            listener(server_event)
