class ServerEvent:
    """
        Server event data sent to registered clients. Currently supports:
        CONNECT_EVENT, DISCONNECT_EVENT, INCOMING_MESSAGE_EVENT, OUTGOING_MESSAGE_EVENT
    """

    CONNECT_EVENT = 'connect'
    DISCONNECT_EVENT = 'disconnect'
    INCOMING_MESSAGE_EVENT = 'incoming'
    OUTGOING_MESSAGE_EVENT = 'outgoing'

    def __init__(self):
        self.event_type = None
        self.server_message = ''

    def __init__(self,event_type):
        self.event_type = event_type
        self.server_message = ''

    def __init__(self,event_type, message):
        self.event_type = event_type
        self.server_message = message

    def get_event_type(self):
        return self.event_type

    def get_message(self):
        return self.server_message