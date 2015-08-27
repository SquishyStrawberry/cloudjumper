#!/usr/bin/env python3
import logging
import re
import socket
import ssl
import time
                            # Same as minecraft
logging.basicConfig(format="[%(asctime)s %(levelname)s]: %(message)s", 
                    datefmt="%H:%M:%S")


class IRCBot(object):
    # https://stackoverflow.com/questions/970545/how-to-strip-color-codes-used-by-mirc-users
    color_finder = "\x1f|\x02|\x12|\x0f|\x16|\x03(?:\d{1,2}(?:,\d{1,2})?)?"
    color_finder = re.compile(color_finder, re.UNICODE)
    logger = logging.getLogger(__name__)

    def __init__(self, user, nick, channel, host, port=None, **kwargs):
        """
            Initializes an IRCBot instance.
            Arguments:
                user: Username to send via the USER command (e.g. Rainbows)
                nick: Nickname to send via the NICK command (e.g. RainbowsN)
                channel: What channel to initially join (e.g. #python)
                host: What host to connect to (e.g. irc.freenode.net)
                port: What port to connect to (e.g. 6667)
            Keyword Arguments:
                check_login: Whether to crash if you don't log in on a registered username.
                fail_after: IDK, Alan please add docs.
                use_ssl: Whether to use SSL, to be more secure.
        """
                
        if port is None:
            port = 6667
            if kwargs.get("use_ssl", False):
                port += 30  # Default SSL port is 6697
        print(port, kwargs.get("use_ssl", False)) 
        self.connection   = (host, port)
        self.user         = user
        self.nick         = nick
        self.base_channel = channel
        self.channel      = None
        self.started      = False
        self.logged_in    = False
        self.check_login  = kwargs.get("check_login", True)
        self.fail_time    = None
        self.fail_after   = kwargs.get("fail_after", 10)
        self.socket       = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if kwargs.get("use_ssl", False):
            self.socket = ssl.wrap_socket(self.socket)
        self.socket.connect(self.connection)
        self.start_up()

    def start_up(self):
        self.logger.debug("[Starting...]")
        while True:
            block = self.get_block()
            if self.handle_ping(block):
                continue
            elif "hostname" in block.lower():
                self.logger.debug("[Set USER and NICK]")
                self.send("USER {0} 0 * :{0}\r\n".format(self.user))
                self.send("NICK {}\r\n".format(self.nick))
            elif "end of /motd" in block.lower():
                self.join_channel(self.base_channel)
                self.started = True
                return

    def join_channel(self, channel):
        self.logger.debug("[Joined Channel {}]".format(channel))
        self.channel = channel
        self.send("JOIN {}\r\n".format(channel))
        time.sleep(2)

    def get_block(self, strip_colors=True):
        message = b""
        while not (b"\n" in message and b"\r" in message):
            message += self.socket.recv(1)
        try:
            message = message.decode()
        except UnicodeError:
            logging.warning("Could not decode message {!r}".format(message))
            message = message.decode("utf-8", "ignore")
        if strip_colors:
            return IRCBot.color_finder.sub("", message)
        else:
            return message

    def send(self, text):
        if not text.endswith("\r\n"):
            text += "\r\n"
        self.socket.send(text.encode())

    def send_message(self, message, recipient=None):
        if recipient is None:
            if self.channel is None:
                raise ValueError("Called send_message without a recipient!")
            recipient = self.channel
        location = "on" if recipient == self.channel else "to" 
        self.logger.info("[{} {} {}] {}".format(self.nick, location, 
                                                recipient, message))
        self.send("PRIVMSG {} :{}\r\n".format(recipient, message))

    def send_action(self, message, recipient=None):
        self.send_message("\u0001ACTION \x0303{}\u0001".format(message), 
                          recipient)

    def handle_block(self, block):
        message_parts = block.split(" ", 1)
        sender = message_parts[0][1:].split("!", 1)[0]
        command = message_parts[1].strip()
        if "throttled: teconnecting too fast" in block.lower():
            raise RuntimeError("Reconnecting too fast!")
        if self.handle_ping(block):
            return {"command": "PING", "message": command[1:]}
        if sender in (self.nick, self.user) or sender == self.connection[0]:
            return {"sender": self.connection[0]}

        message_info = command.split(" ", 2)
        command, recipient = message_info[:2]
        if len(message_info) >= 3:
            message = message_info[2][1:]
        else:
            message = ""

        # Are there any other commands I need to handle?
        if command.upper() in ("PRIVMSG", "ALERT"):
            location = "on" if recipient == self.channel else "to"
            self.logger.info("[{} {} {}] {}".format(sender, location, 
                                                    recipient, message))
        if sender.lower() == "nickserv":
            clear_message = "".join(i for i in message if i.isalnum() or i.isspace()).lower()
            if clear_message == "syntax register password email":
                raise ValueError("Network requires both password and email!")
            elif "this nickname is registered" in clear_message and self.check_login and not self.logged_in:
                self.logger.debug("[Registered Nickname]")
                self.fail_time = time.time()

        return {"command": command, "sender": sender, "recipient": recipient, "message": message}

    def handle_ping(self, message):
        is_ping = message.upper().startswith("PING")
        if is_ping:
            self.logger.debug("[Responded To Ping]")
            data = "".join(message.split(" ", 1)[1:])[1:]
            self.send("PONG :{}\r\n".format(data))
        return is_ping

    def leave_channel(self, message=None):
        self.logger.debug("[Left Channel {} with reason '{}']".format(self.channel, 
                                                                      message))
        quit_message = (" :" + message) if message is not None else None
        self.send("PART {}{}\r\n".format(self.channel, quit_message or ""))

    def run(self):
        self.logger.debug("[Started Running]")
        while self.started:
            if self.started and self.channel is None:
                self.join_channel(self.base_channel)
            if self.check_login and self.fail_time is not None and time.time() - self.fail_time >= self.fail_after:
                raise IRCError("Need to login on a registered username!")
            msg = self.get_block()
            msg_data = self.handle_block(msg)
            if msg_data:
                self.extra_handling(msg_data)

    def register(self, password, email=None, login=False):
        self.logger.debug("[Registered]")
        if not self.logged_in:
            self.fail_time = None
            send = "REGISTER " + password
            if email is not None:
                send += " " + email
            self.send_message(send, "nickserv")
            if login:
                self.login(password)

    def login(self, password):
        self.logger.debug("[Logged In]")
        if not self.logged_in:
            send = "IDENTIFY " + password
            self.send_message(send, "nickserv")
            self.logged_in = True
            self.fail_time = None

    def extra_handling(self, block_data):
        return block_data

    def quit(self, message):
        self.logger.debug("[Quit]")
        self.leave_channel(message)
        self.started = False
        self.socket.close()

