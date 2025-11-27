class ServerMessage:

    def __init__(self, message):
        self.message = message
        self.tokens = message.split(" ")
        self.start_index = 0 if message.startswith(":") else -1
        self.command_index = self.start_index + 1
        self.message_type = self.tokens[self.command_index].upper()

    def get_message_type(self):
        return self.message_type

    def get_raw_message(self):
        return self.message

    def is_ping(self):
        return self.message_type == "PING"

    def is_privmsg(self):
        return self.message_type == "PRIVMSG"
