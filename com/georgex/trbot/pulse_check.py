import threading
import time
from datetime import datetime

class PulseCheck:
    """
    Pulse Check class
        Checks periodically if the connection to the IRC server is still alive.  Fires a LostConnection event
        when the connection to the IRC server is lost.
    """
    def __init__(self, last_heart_beat_time, max_seconds_without_ping, max_ping_requests):
        '''
        Constructor
            last_heart_beat_time: the last time the IRC server sent a PING or responded with a PONG. When the bot starts
            this field is initialized to the start time.

            check_frequency: how often the connection to the IRC server is checked.  This value is to be specifed in seconds.
        '''
        self.last_heart_beat_time = last_heart_beat_time
        self.max_seconds_without_ping = max_seconds_without_ping

        self.pulse_check_listeners = []
        self.ping_token = ''
        self.ping_count = 0
        self.time_since_last_hearbeat = 0
        self.max_ping_requests = max_ping_requests

    def start_pulse_check(self):
        self.message_thread = threading.Thread(target=self.monitor_pulse, daemon=True)
        self.message_thread.start()

    def monitor_pulse(self):
        """
        Checks periodically if the connection to the IRC server is still alive.
        """
        while (True):
            time.sleep(self.max_seconds_without_ping)
            #secs = round(self.time_since_last_hearbeat, 0)
            if (self.is_likely_connected()):
                info_event = InfoEvent(f"Connection is alive; time since last heart beat: {self.time_since_last_hearbeat}")
                self.fire_pulse_check_event(info_event)
                continue;
            '''
            while (self.ping_count < self.max_ping_requests):
                self.ping_token = time.time()
                ping_request_event = PingRequestEvent(self.ping_token)
                self.fire_pulse_check_event(ping_request_event)
                self.ping_count += 1
                info_event = InfoEvent("Sent PING")
                time.sleep(30) # wait for 30 seconds to see if we get a response
                if (self.is_likely_connected()):
                    info_event = InfoEvent("Server has responded to client PING")
                    self.fire_pulse_check_event(info_event)
                    break;
                time.sleep(120) #wait two minutes for another PING attempt

            if (self.ping_count < self.max_ping_requests):
                continue;
            break;
            '''

        info_event = InfoEvent("Connection to server has been lost")
        self.fire_pulse_check_event(info_event)
        lost_connection_event = LostConnectionEvent()
        self.fire_pulse_check_event(lost_connection_event)

    def is_likely_connected(self):
        current_datetime = datetime.now()
        self.time_since_last_hearbeat = current_datetime - self.last_heart_beat_time
        #print('Pulse check: time diff: ' + str(time_diff) + ' seconds')
        return self.time_since_last_hearbeat.total_seconds() < self.max_seconds_without_ping

    def register_pulse_check_listener(self, pulse_check_listener):
        self.pulse_check_listeners.append(pulse_check_listener)
        return

    def fire_pulse_check_event(self, event):
        for listener in self.pulse_check_listeners:
            listener(event)

    def on_pong_response(self, token):
        '''
        When a response is received to a generated PING request, the last heart beat time is set to the current time.
        '''
        if (token == self.ping_token):
            self.last_heart_beat_time = datetime.now()

    def set_last_heart_beat_time(self, heart_beat_time):
        '''
        Whenever a PING is received from the server, the last heart beat time is set afresh
        '''
        self.last_heart_beat_time = heart_beat_time

class PingRequestEvent:
    """
    Event object for requesting a server PING.
    """
    def __init__(self, ping_token):
        """
        Constructor
        ping_token: the token to be sent with the PING.
        """
        self.ping_token = ping_token

    def get_ping_token(self):
        """
        Returns the PING token.
        """
        return self.ping_token

class LostConnectionEvent:
    '''
    Event object for notifying listeners of lost connections.
    '''
    def __init__(self):
        pass

class InfoEvent:
    '''
    InfoEvent to generate messages for logging.
    '''
    def __init__(self, info):
        self.info = info

    def get_info(self):
        return self.info