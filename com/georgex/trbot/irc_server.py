import socket
import ssl
import sys
import threading
import time
import traceback
from datetime import datetime

import com.georgex.trbot.pulse_check
from com.georgex.trbot.chat_message import ChatMessage
from com.georgex.trbot.irc_command import IrcCommand
from com.georgex.trbot.server_event import ServerEvent
from com.georgex.trbot.server_message import ServerMessage
from com.georgex.trbot.translator import Translator
from com.georgex.trbot.command.bot_command_factory import BotCommandFactory
from com.georgex.trbot.pulse_check import PulseCheck
from com.georgex.trbot.client_stats import ClientStats

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
        self.server_event_listener_list = []
        self.pulse_check_event_listener_list = []
        self.ping_count = 0
        self.start_time = None
        self.last_pong_time = None
        self.irc_command = None
        self.translator = Translator()
        self.translator.set_libre_url(app_config.get_libre_translate_url())


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
        self.pulse_check = PulseCheck(self.start_time, int(self.app_config.get_max_seconds_without_ping()), int(self.app_config.get_max_ping_tries()))
        self.pulse_check.register_pulse_check_listener(self.on_pulse_check_event)
        self.pulse_check.set_last_heart_beat_time(self.start_time)
        self.pulse_check.start_pulse_check()
        ClientStats.start_time = self.start_time

    def process_message(self):
        """
        Process messages received from IRC server. Runs in a separate thread that starts after connecting to the IRC server.
        """
        while self.is_connected:
            try:
                for message in self.message_stream:
                    self.server_message = ServerMessage(message.strip())
                    message_event = ServerEvent(ServerEvent.INCOMING_MESSAGE_EVENT, self.server_message)
                    self.fire_server_event(message_event)
                    if (self.server_message.is_pong()):
                        pong_token = f"{message[6:].strip()}"
                        self.on_pong(pong_token)
                        continue
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

    def on_pulse_check_event(self, pulse_check_event ):
        '''
        Event handler for pulse check events.
        :param pulse_check_event: the pulse check event which can be a PING request or a lost connection event.
        '''
        if (isinstance(pulse_check_event, com.georgex.trbot.pulse_check.PingRequestEvent)):
            self.irc_command.ping(pulse_check_event.ping_token)
            return
        if (isinstance(pulse_check_event, com.georgex.trbot.pulse_check.InfoEvent)):
            self.fire_pulse_check_event(pulse_check_event)

    def on_pong(self, pong_token):
        '''
        Handler function called when a PONG response is received from the server.
        :param pong_token: the PONG response from the server
        '''
        self.pulse_check.on_pong_response(pong_token)
        return

    def onPing(self, token):
        """
        PING message handler.
        :param token: the token to be used for the PONG response
        :return: the PONG response sent to the server
        """
        self.pulse_check.set_last_heart_beat_time(datetime.now())
        pong_command = self.irc_command.pong(token)
        self.ping_count += 1
        ClientStats.ping_count += 1
        self.fire_server_event(ServerEvent(ServerEvent.OUTGOING_MESSAGE_EVENT, pong_command))
        return pong_command

    def onChatMessage(self, message):
        """
        PRIVMSG message handler.
        :param message: the PRIVMSG message received from the IRC server
        :return: the translated PRIVMSG message sent to the server
        """
        chat_message = ChatMessage(message)
        is_source_channel = self.is_source_channel(chat_message.get_channel())
        is_target_channel = self.is_target_channel(chat_message.get_channel())
        if (not (is_source_channel or is_target_channel) ):
            return
        if (chat_message.is_bot_command(self.nickname)):
            self.onBotCommand(chat_message)
            return
        if (not is_source_channel):
            return;
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
        '''
        Handler function called when a PRIVMSG contains a bot command.
        :param chat_message: the PRIVMSG message received from the IRC server
        '''
        bot_command = BotCommandFactory().getCommand(chat_message)
        bot_command.set_app_config(self.app_config)
        responses = bot_command.execute()
        for response in responses:
            chat_command = self.irc_command.chat_message(self.nickname, chat_message.get_channel(), response)
            self.fire_server_event(ServerEvent(ServerEvent.OUTGOING_MESSAGE_EVENT, chat_command))

    def send_to_xlate_channel(self, nick, message):
        '''
        Send a translated message to the target channel.
        :param nick: the nickname sending the message
        :param message: the message to be sent to the target channel
        '''
        message_to_send = nick + " says: " + message
        chat_command = self.irc_command.chat_message(self.nickname, self.target_channel, message_to_send)
        self.fire_server_event(ServerEvent(ServerEvent.OUTGOING_MESSAGE_EVENT, chat_command))
        ClientStats.message_count += 1

    def is_source_channel(self, channel):
        '''
        Returns True if the channel is in the source channel, i.e., the channel whose messages are to be translated.
        '''
        source_channel = self.app_config.get_source_channel() if self.app_config.get_source_channel().startswith("#") else "#" + self.app_config.get_source_channel()
        current_channel = channel if channel.startswith("#") else "#" + channel()
        return current_channel.lower() == source_channel.lower()

    def is_target_channel(self, channel):
        '''
        Returns true if the channel is the target channel, i.e., the channel to which translated messages are sent.
        '''
        target_channel = self.app_config.get_target_channel() if self.app_config.get_target_channel().startswith("#") else "#" + self.app_config.get_target_channel()
        current_channel = channel if channel.startswith("#") else "#" + channel()
        return current_channel.lower() == target_channel.lower()

    def disconnect(self):
        """ Disconnect from IRC server """
        #self.show_message('isConnected set to False')
        self.is_connected = False
        self.irc_socket.close();
        #self.message_thread.join()

    def connected(self):
        '''
        Returns True if there is a live connection to IRC server. False otherwise.
        '''
        return self.is_connected

    def register_server_event_listener(self, server_event_listener):
        """
        Register a server event listener.
        :param server_event_listener: the listener to be registered
        :return: None
        """
        self.server_event_listener_list.append(server_event_listener)

    def fire_server_event(self, server_event):
        '''
        Fire server events to registered listeners.
        :param server_event: the server event to be fired
        '''
        for listener in self.server_event_listener_list:
            listener(server_event)

    def register_pulse_check_event_listener(self, pulse_check_event_listener):
        '''
        Register listeners for pulse check events.
        '''
        self.pulse_check_event_listener_list.append(pulse_check_event_listener)

    def fire_pulse_check_event(self, pulse_check_event):
        '''
        Fire pulse check events to registered listeners.
        :param pulse_check_event: the pulse check event to be fired
        '''
        for listener in self.pulse_check_event_listener_list:
            listener(pulse_check_event)