"""The networking client code."""
import hashlib
# import logging
import pickle
import socket
from kivy.logger import Logger

from random import randint
from socket import SHUT_RDWR
import time
from time import sleep
from models.game import Game
from mwt import MWT


class NetClient():
    """The networking worker for the chess client.

    Attributes:
        host (String): The hostname or IP of the chess server
        logged_in (bool): Is the user logged in or not
        port (Integer): The port of the chess server

    """

    def __init__(self, host, port):
        """Initialize a client connection to a chess server.

        Args:
            host (String): The hostname or IP to connect to
            port (Integer): The portnumber to connect to
        """
        self.logger = Logger
        self.logger.debug('__init__')
        self.host = host
        self.port = int(port)
        self._connect_to_server()
        self.logged_in = False
        self._uguid = None

    def _connect_to_server(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.good_server_connection = False
        try:
            self._socket.connect((self.host, self.port))
            self.good_server_connection = True
            return True
        except ConnectionRefusedError as e:
            return False

    def _send(self, cmd):
        """Send a command to the server and return the raw result.

        Args:
            cmd (String): The command to send to the server

        Returns:
            String: The raw result from the server

        """
        if len(cmd) < 1:
            return None
        if self.logged_in:
            cmd += f"|{self._uguid}"

        self._connect_to_server()
        if not self.good_server_connection:
            self.logger.error("Connection lost!!")
            return None
        self.logger.debug(f"Sending: {cmd}")
        # total data partwise in an array
        total_data = []
        data = ''
        try:
            self._socket.sendall(cmd.encode("utf8"))
        except ConnectionResetError:
            self._connect_to_server()
            self._socket.sendall(cmd.encode("utf8"))

        # beginning time
        start = time.time()
        while 1:
            data = self._socket.recv(4096)
            if len(data) > 0:
                total_data.append(data)
                sleep(0.01)
            else:
                # Done receiving
                break

        took = time.time() - start
        self.logger.debug(f"Response took: {took}")

        # join all parts to make final string
        return b''.join(total_data)

    def _getString(self, cmd):
        """Send a command to the server and return the response as a String.

        Args:
            cmd (String): The command to send

        Returns:
            String: The result from the server as a String

        """
        data = self._send(cmd)
        return data.decode("utf8")

    def _getObject(self, cmd):
        """Send a command to the server and return a pickled object.

        Args:
            cmd (String): the command to send

        Returns:
            object: A object from the server (pickled)

        """
        data = self._send(cmd)
        return pickle.loads(data)

    def queue_up_new_game(self, blocking=True):
        """Request a new game from the server against a random player.

        Returns:
            String: The guid of the new game

        """
        if self.logged_in is False or self._uguid is None:
            return False
        cmd = 'queue_up'
        game_id = self._getString(cmd)
        if blocking:
            while game_id == 'queued_for_game':
                self.logger.info('Waiting for game...')
                st = randint(1, 3)
                sleep(st)
                game_id = self._getString(cmd)
        return game_id

    def dequeue(self):
        cmd = 'dequeue'
        return self._getString(cmd)

    def game_state(self, gguid):
        cmd = f"getboardstate|{gguid}"
        state = self._getObject(cmd)
        return state

    def is_it_my_turn(self, gguid):
        cmd = f"myturn|{gguid}"
        result = self._getString(cmd)
        return result == "True"

    def make_move(self, gguid, move):
        cmd = f"move|{gguid}|{move}"
        result = self._getString(cmd)
        if result == "move_made":
            return True
        else:
            return result

    def opponent_name(self, gguid):
        cmd = f"opponent_name|{gguid}"
        result = self._getString(cmd)
        return result

    @MWT(timeout=15)
    def my_side(self, gguid):
        cmd = f"myside|{gguid}"
        result = self._getString(cmd)
        return result

    def get_board(self, gguid):
        cmd = f"getboard|{gguid}"
        board = self._getObject(cmd)
        return board

    @MWT(timeout=5)
    def current_games(self):
        if self.logged_in is False or self._uguid is None:
            return []
        cmd = "current_games"
        gguids = self._getString(cmd).split("|")
        games = []
        for guid in gguids:
            if len(guid) > 0:
                games.append(Game(guid, self))
        return games

    @MWT(timeout=5)
    def done_games(self):
        if self.logged_in is False or self._uguid is None:
            return []
        cmd = "done_games"
        gguids = self._getString(cmd).split("|")
        games = []
        for guid in gguids:
            if len(guid) > 0:
                games.append(Game(guid, self))
        return games

    @MWT(timeout=5)
    def all_games(self):
        if self.logged_in is False or self._uguid is None:
            return []
        cmd = "all_games"
        gguids = self._getString(cmd).split("|")
        games = []
        for guid in gguids:
            if len(guid) > 0:
                games.append(Game(guid, self))
        return games

    def login(self, username, password):
        """Send a login request to the server.

        Args:
            username (String): The username
            password (String): The unhashed password

        Returns:
            Boolean: True if login was succesful, else False

        """
        if self.logged_in and self._uguid is not None:
            return True
        # Bad server connection?
        if not self.good_server_connection and not self._connect_to_server():
            return False
        # Send the login information to the server and see if we are correct
        hashed_password = hashlib.sha224(password.encode("utf8")).hexdigest()
        cmd = f"login|{username}|{hashed_password}"
        guid = self._getString(cmd)
        if guid == "invalid":
            return False
        else:
            self.logger.debug(f"Setting guid; {guid}")
            self.logged_in = True
            self._uguid = guid
            return True

    def register(self, username, password, password_confirm):
        cmd = f"register|{username}|{password}|{password_confirm}"
        result = self._getString(cmd)
        if result == "username_taken":
            return "username_taken"
        if result == "invalid_password":
            return "invalid_password"
        if result.startswith("register_success"):
            guid = result.split("|")[1]
            self.logged_in = True
            self._uguid = guid
            return True
