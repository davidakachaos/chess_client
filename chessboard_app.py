# Kivy imports
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.resources import resource_find
from kivy.logger import Logger
# Other imports
import os
# import views
from screens.chess_game import ChessGame, GameScreen
from screens.login import Login
from screens.games_overview import GamesOverview
from screens.register import Register
from mwt import MWT
if __name__ == '__main__':
    from kivy.garden.notification import Notification


class ChessboardApp(App):
    username = StringProperty(None)
    password = StringProperty(None)
    host_address = StringProperty("127.0.0.1")
    host_port = StringProperty("2004")
    player = ObjectProperty(None)
    manager = ObjectProperty(None)

    my_turn_games = []
    opp_turn_games = []
    old_games = []

    def check_background_games(self, *args):
        """Check if there are changes to any current games for this player."""
        if self.username is None or self.password is None:
            return
        if self.player.logged_in is False:
            return
        if not self.my_turn_games and not self.old_games and not self.opp_turn_games:
            self.load_current_games()

        games = list(self.player.current_games)
        if len(games) < 1:
            return

        for game in games:
            if game.over and game in self.old_games:
                # NOOP
                pass
            elif game.over and game not in self.old_games:
                Logger.info(f"Game over and not in old games? {game.guid}")
                self.notify_removed_game(game)
                self.old_games.append(game)
                if game in self.opp_turn_games:
                    self.opp_turn_games.remove(game)
                if game in self.my_turn_games:
                    self.my_turn_games.remove(game)

            elif game.my_turn and game in self.opp_turn_games:
                # New game for us to make a move!
                self.notify_my_move(game)
                self.my_turn_games.append(game)
                self.opp_turn_games.remove(game)
            elif not game.my_turn and game in self.my_turn_games:
                # Opponent is to move now.
                self.opp_turn_games.append(game)
                self.my_turn_games.remove(game)
            elif game not in self.my_turn_games and game not in self.opp_turn_games:
                self.notify_new_game(game)
                if game.my_turn:
                    self.my_turn_games.append(game)
                else:
                    self.opp_turn_games.append(game)

    def load_current_games(self):
        Logger.info("Loading games for current player...")
        games = list(self.player.all_games)
        self.my_turn_games = [
            game for game in games if game.my_turn and not game.over]
        self.opp_turn_games = [
            game for game in games if not game.my_turn and not game.over]
        self.old_games = [game for game in games if game.over]

    def notify_new_game(self, game):
        Notification().open(
            title='Nieuw spel gestart!',
            message=f"Er is een nieuw spel begonnen tegen {game.my_opponent}.",
            timeout=5,
            icon=resource_find('data/logo/kivy-icon-128.png')
            # on_stop=partial(self.printer, 'Notification closed')
        )

    def notify_my_move(self, game):
        Notification().open(
            title='Uw beurt!',
            message=f"Het is uw beurt in een spel tegen {game.my_opponent}.",
            timeout=5,
            icon=resource_find('data/logo/kivy-icon-128.png')
            # on_stop=partial(self.printer, 'Notification closed')
        )

    def notify_removed_game(self, game):
        Notification().open(
            title='Spel beëindigd!',
            message=f"Spel beëindigd tegen {game.my_opponent}.\nResultaat: {game.over_reason}",
            timeout=5,
            icon=resource_find('data/logo/kivy-icon-128.png')
            # on_stop=partial(self.printer, 'Notification closed')
        )

    def build(self):
        Window.size = (1046, 718)
        self.manager = ScreenManager()

        # Add screens to app
        self.manager.add_widget(Login(name='login'))
        self.manager.add_widget(Register(name='registration'))
        self.manager.add_widget(GamesOverview(name="overview"))

        game = ChessGame()
        game.draw_board()
        # game.update_board(board)
        # game.setup_clocks(time=60, interval=.01)

        game_screen = GameScreen(name='game')
        game_screen.add_widget(game)

        self.manager.add_widget(game_screen)

        self.manager.current = 'login'

        Config.set('graphics', 'resizable', '1')
        Config.write()
        # Notifications...
        Clock.schedule_interval(self.check_background_games, 2)
        Clock.schedule_interval(MWT().collect, 1)

        return self.manager

    def get_application_config(self):
        if not self.username:
            return super(ChessboardApp, self).get_application_config()

        conf_directory = self.user_data_dir + '/' + self.username

        if not os.path.exists(conf_directory):
            os.makedirs(conf_directory)

        return super(ChessboardApp, self).get_application_config(
            '%s/config.cfg' % (conf_directory)
        )


if __name__ == '__main__':
    ChessboardApp().run()
