class IrcCommand:
    """
    IrcCommand manages client commands to the IRC server.
    """

    def __init__(self, secure_socket):
        """
        Constructor
        :param secure_socket: a secure socket object that represents the IRC server connection.
        """
        self.secure_socket = secure_socket

    def ping(self, token):
        command = f"PING :{token}"
        self.send_command(command)
        return command

    def get_join_command(self, channel):
        """
        Returns a JOIN channel command that can be sent to the IRC server.
        :param channel: the name of the channel to join
        :return: the JOIN command for the specified channel
        """
        return f"JOIN {channel}" if channel.startswith("#") else f"JOIN #{channel}"

    def join_channel(self, channel):
        """
        Sends a JOIN channel command to the IRC server.
        :param channel: the name of the channel to join
        :return: None
        """
        command = self.get_join_command(channel)
        print(f"Join command: {command}")
        self.send_command(command)

    def pong(self, token):
        """
        Sends a PONG command to the IRC server.
        :param token: the token received from the IRC server in the PING message
        :return: the PONG command sent to the IRC server
        """
        command = f"PONG {token}"
        self.send_command(command)
        return command

    def chat_message(self, nick, channel, message):
        """
        Sends a chat message to the IRC server.
        :param nick: the nickname of the current user
        :param channel: the name of the channel to send the message to
        :param message: the message to send
        :return: None
        """
        command = f":{nick}! PRIVMSG  {channel} :{message}" if channel.startswith("#") else f":{nick}! PRIVMSG #{channel} :{message}"
        executed_command = self.send_command(command)
        return command

    def send_command(self, command):
        """
        Sends the specified command to the IRC server.
        :param command: the command to send
        :return: None
        """
        command_to_send = command + "\n"
        command_bytes = command_to_send.encode('utf-8')
        self.secure_socket.send(command_bytes)


