from datetime import datetime

import com
from com.georgex.trbot.server_event import ServerEvent

class ClientConsole:

    def __init__(self):
        self.server_event = None
        self.date_formatter = '%Y-%m-%d %H:%M:%S'

    def on_server_event(self, server_event):
        self.server_event = server_event
        if (self.server_event.get_event_type() == ServerEvent.INCOMING_MESSAGE_EVENT):
            self.show_incoming_message(self.server_event.get_message())
            return;
        if (self.server_event.get_event_type() == ServerEvent.OUTGOING_MESSAGE_EVENT):
            self.show_outgoing_message(self.server_event.get_message())
            return;

    def show_incoming_message(self, msg):
        now = datetime.now()
        formatted_datetime = now.strftime(self.date_formatter)
        print(f"{formatted_datetime}: INCOMING: {msg.get_raw_message()}")

    def show_outgoing_message(self, msg):
        now = datetime.now()
        formatted_datetime = now.strftime(self.date_formatter)
        print(f"{formatted_datetime}: OUTGOING: {msg}")

    def on_pulse_check_event(self, pulse_check_event):
        if (isinstance(pulse_check_event, com.georgex.trbot.pulse_check.InfoEvent)):
            now = datetime.now()
            formatted_datetime = now.strftime(self.date_formatter)
            print(f"{formatted_datetime}: PULSE CHECK: {pulse_check_event.get_info()}")