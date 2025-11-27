from datetime import datetime

from com.georgex.trbot.server_event import ServerEvent

class ClientConsole:

    def __init__(self):
        self.server_event = None

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
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{formatted_datetime}: INCOMING: {msg.get_raw_message()}")

    def show_outgoing_message(self, msg):
        now = datetime.now()
        formatted_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{formatted_datetime}: OUTGOING: {msg}")