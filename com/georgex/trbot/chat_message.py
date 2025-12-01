from server_message import ServerMessage

class ChatMessage(ServerMessage):
    """
        Parses PRIVMSG message received from IRC server
    """
    def __init__(self, raw_message):
        super().__init__(raw_message)
        self.channel_index = self.start_index + 2
        self.channel = self.tokens[self.channel_index]
        self.chat_message_index = self.start_index + 3
        self.chat_message = self.parse_message()
        self.sender_nick_index = self.start_index + 0;
        self.sender_nick = self.get_sender_nick()

    def parse_message(self):
        message_start =  self.tokens[self.chat_message_index]
        index = self.get_raw_message().index(message_start)
        message = self.get_raw_message()[index+1:]
        return message

    def get_channel(self):
        return self.channel

    def get_chat_message(self):
        return self.chat_message

    def get_sender_nick(self):
        return self.sender_nick

    def get_sender_nick(self):
        token0 = self.tokens[self.sender_nick_index]
        nick = token0[1:]
        index = nick.index("!")
        nick = nick[0:index]
        return nick

    def is_bot_command(self, bot_nick):
        return self.chat_message.startswith('!' + bot_nick)

    def is_private_message(self):
        """
        Returns true if this message is from a nick and not a channel.
        :return: Boolean
        """
        return not self.channel.startswith("#")

# chat message format
#:asi9!~cIRCus_us@67d1-b010-aead-c355-1d2c.nj.comcast.net PRIVMSG #test4 :hello all