from .game import Game
from networking.client import NetClient
from mwt import MWT

class Player(object):
    """A chess player"""
    def __init__(self, login, password=None, host_address="127.0.0.1", host_port="2004"):
        self.net = NetClient(host_address, host_port)
        self.login = login
        self.password = password
        self._games = []

        if self.password:
            self.net.login(login, password)
        if self.net.logged_in:
            self._games = self.net.current_games()

    @property
    def current_games(self):
        return self._games

    @property
    def logged_in(self):
        return self.net.logged_in

    def do_login(self):
        if self.password:
            return self.net.login(self.login, self.password)

    @MWT(timeout=5)
    def load_games_from_server(self):
        if self.net.logged_in:
            self._games = self.net.current_games()

    def register(self, password_confirm):
        return self.net.register(self.login, self.password, password_confirm)
