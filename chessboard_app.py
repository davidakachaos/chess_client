# Kivy imports
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.resources import resource_find
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

    def check_background_games(self, *args):
        """Check if there are changes to any current games for this player."""
        if self.username is None or self.password is None:
            return
        if self.player.logged_in is False:
            return

        before_load = list(self.player.current_games)
        current_my_turn = [game for game in before_load if game.my_turn]
        self.player.load_games_from_server()
        after_load = list(self.player.current_games)
        new_my_turn = [game for game in after_load if game.my_turn]
        my_turn = [game for game in new_my_turn if game not in current_my_turn]
        new_games = [game for game in after_load if game not in before_load]
        removed_games = [
            game for game in before_load if game not in after_load]

        if my_turn:
            print(f"We found new my turn?? {my_turn}")
            for game in my_turn:
                self.notify_my_move(game)

        if new_games:
            print(f"We found new games?? {new_games}")
            for game in new_games:
                self.notify_new_game(game)

        if removed_games:
            print(f"There are games who ended? {removed_games}")
            for game in removed_games:
                self.notify_removed_game(game)

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
            title='Jouw beurt!',
            message=f"Het is jouw beurt in een spel tegen {game.my_opponent}.",
            timeout=5,
            icon=resource_find('data/logo/kivy-icon-128.png')
            # on_stop=partial(self.printer, 'Notification closed')
        )

    def notify_removed_game(self, game):
        Notification().open(
            title='Spel beëindigd!',
            message=f"Er is een spel beëindigd tegen {game.my_opponent}. Resultaat: {game.state['result']}",
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
