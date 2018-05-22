# Kivy imports
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.screenmanager import SlideTransition
from kivy.uix.textinput import TextInput
from kivy.resources import resource_find
from kivy.garden.notification import Notification
# Chess imports
import chess
import chess.uci
# Other imports
import os
import string
import threading
from functools import partial
from login import Login
from games_overview import GamesOverview
# Models import
from models.player import Player
from models.game import Game

board = None  # chess.Board()
# No need for a computer opponent
# engine = chess.uci.popen_engine("stockfish")

data_dir = 'data/'
image_dir = data_dir + 'images/'
cp_images = image_dir + 'chess-pieces/'
other_images = image_dir + 'other/'


class Chessboard(GridLayout):
    def gen_image_dict(self, *args, image_dir=cp_images):
        if image_dir[-1] != '/':
            image_dir += '/'
        d = {'p': image_dir + 'BlackPawn.png',
             'r': image_dir + 'BlackRook.png',
             'n': image_dir + 'BlackKnight.png',
             'b': image_dir + 'BlackBishop.png',
             'q': image_dir + 'BlackQueen.png',
             'k': image_dir + 'BlackKing.png',
             'P': image_dir + 'WhitePawn.png',
             'R': image_dir + 'WhiteRook.png',
             'N': image_dir + 'WhiteKnight.png',
             'B': image_dir + 'WhiteBishop.png',
             'Q': image_dir + 'WhiteQueen.png',
             'K': image_dir + 'WhiteKing.png',
             }
        return d

    def update_positions(self, *args):
        # Can't call ids directly for some reason so ...
        # Dictionary mapping ids to children (Chess cells)
        ids = {child.id: child for child in self.children}
        Logger.info(f"Loading board FEN; {board.fen()}")
        # Get the board positions from the fen
        b = str(board.fen).split()[4].replace('/', '')[7:]
        # Replace empty spaces with dots
        for num in range(1, 10):
            b = b.replace(str(num), '.'*num)

        # Generate dictionary that maps pieces to images
        image_dict = self.gen_image_dict()

        # Map Chess cell ids to board positions
        for x in zip(range(64), list(b)):
            if x[1] != '.':
                image = image_dict[x[1]]
            else:
                image = other_images + 'transparency.png'
            ids[str(x[0])].children[0].source = image

    def highlight_chesscell(self, id_list, *args):
        self.update_positions()
        ids = {child.id: child for child in self.children}
        highlight_image = other_images + 'highlight.png'
        for id in id_list:
            ids[str(id)].children[0].source = highlight_image

    def on_size(self, *args):
        board_dimensions = sorted([self.width, self.height])[0]

        self.row_force_default = True
        self.col_force_default = True

        self.row_default_height = board_dimensions/self.rows
        self.col_default_width = board_dimensions/self.columns

    def button_down(self, id, *args):
        ids = {child.id: child for child in self.children}

        background_down = 'atlas://data/images/defaulttheme/button_pressed'
        ids[id].background_normal = background_down

    def button_up(self, id, *args):
        ids = {child.id: child for child in self.children}

        background_normal = 'atlas://data/images/defaulttheme/button'
        ids[id].background_normal = background_normal

    def press_button(self, id, *args, is_engine_move=False, engine_move=''):
        id = str(id)
        self.button_down(id)

        if is_engine_move is False:
            Clock.schedule_once(partial(self.button_up, id), .7)
        else:
            Clock.schedule_once(partial(self.button_up, id), .3)
            # board.push(engine_move)
            Clock.schedule_once(self.update_positions)

    def engine_move(self, move, *args):
        ids = {child.id: child for child in self.children}
        starter_pos = move[0]
        current_pos = move[1]

        self.press_button(starter_pos)


class ChessboardCentered(BoxLayout):
    def on_size(self, *args):
        board_dimensions = sorted([self.width, self.height])[0]
        self.padding = [(self.width-board_dimensions)/2,
                        (self.height-board_dimensions)/2, 0, 0]


class ChessCell(Button):
    pass


class Sidebar(FloatLayout):
    pass


class ChessClockContainer(BoxLayout):
    pass


class GameButtonContainer(BoxLayout):
    pass


class GameButton(Button):
    pass


class BlackChessClock(BoxLayout):
    pass


class ChessClockDisplay(TextInput):
    pass


class ChessClockButton(Button):
    pass


class WhiteChessClock(BoxLayout):
    pass


class Movebox(BoxLayout):
    pass


class ChessGame(BoxLayout):
    selected_square = None

    movebox_moves = StringProperty()

    black_time = StringProperty()
    white_time = StringProperty()

    player = ObjectProperty()
    game_instance = ObjectProperty()

    time_interval = 0.5

    def id_to_square(self, id, *args):
        id = int(id)
        row = abs(id//8 - 8)
        column = id % 8
        return (row-1) * 8 + column

    def id_to_san(self, id, *args):
        id = int(id)
        row = abs(id//8 - 8)
        column = list(string.ascii_lowercase)[id % 8]
        return column + str(row)

    def san_to_id(self, san, *args):
        column = san[0]
        row = int(san[1])
        id_row = 64 - (row * 8)
        id_column = list(string.ascii_lowercase).index(column)
        id = id_row + id_column
        return id

    def create_legal_move_dict(self, *args):
        legal_moves = list(self.game_instance.board.legal_moves)
        legal_move_dict = {}
        for move in legal_moves:
            move = str(move)
            if move[:2] in legal_move_dict:
                legal_move_dict[move[:2]] = \
                    legal_move_dict[move[:2]] + [move[2:]]
            else:
                legal_move_dict[move[:2]] = [move[2:]]

        return legal_move_dict

    def draw_board(self, *args):
        for child in self.children:
            Logger.debug(f"Child: {child}")
            if type(child) == ChessboardCentered:
                c_board = child.children[0]

        for num in range(64):
            button = ChessCell(id=str(num))
            c_board.add_widget(button)

    def update_board(self, *args):
        global board
        board = self.game_instance.board
        self.ids.board.update_positions(self.game_instance.board)
        # Adjust the move list displayed
        self.update_moves_list()

    def update_moves_list(self):
        def grouped(iterable, n):
            "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
            return zip(*[iter(iterable)]*n)
        move = 1
        moves = ""
        for white_move, black_move in grouped(list(self.game_instance.board.move_stack), 2):
            moves += f"{move}. {str(white_move)}\t\t{str(black_move)}\n"
            move += 1
        self.movebox_moves += f"\n{moves}"

    def select_piece(self, id, *args):
        if not self.game_instance.my_turn:
            Logger.info("Not our time to make a move yet!")
            self.selected_square = None
            return False

        square_num = self.id_to_square(id)
        square_san = self.id_to_san(id)
        piece = board.piece_at(square_num)

        legal_move_dict = self.create_legal_move_dict()

        if square_san in legal_move_dict:
            id_list = []
            for move in legal_move_dict[square_san]:
                id_list.append(self.san_to_id(move))
            self.ids.board.highlight_chesscell(id_list)
        self.selected_square = id

    def move_piece(self, id, *args):
        legal_move_dict = self.create_legal_move_dict()
        legal_ids = []
        try:
            for san in legal_move_dict[
                    self.id_to_san(self.selected_square)]:
                legal_ids.append(self.san_to_id(san))
        except KeyError:
            pass

        if int(id) in legal_ids:
            original_square = self.id_to_san(self.selected_square)
            current_square = self.id_to_san(id)
            move = original_square + current_square
            # Word door de server gedaan;
            # chess.Move.from_uci(original_square + current_square)

            if self.game_instance.make_move(move):
                self.update_board()
                self.selected_square = None

            # try:
            #     self.white_time_counter(cancel=True)
            # except NameError:
            #     pass

            if not self.game_end_check():
                Clock.schedule_once(self.await_turn)

        else:
            self.update_board()
            self.select_piece(id)

    def await_turn(self, *args):
        if self.game_instance.my_turn:
            self.movebox_moves = "Zelf aan zet"
            Logger.info("Opponent made a move!!")
            global board
            board = self.game_instance.board
            self.update_moves_list()
            # Last move was made by the other side
            engine_move = self.game_instance.board.move_stack[-1]
            str_move = str(engine_move)
            move = [self.san_to_id(x) for x in [str_move[:2], str_move[2:]]]

            self.ids.board.press_button(move[0])
            self.select_piece(move[0])
            Clock.schedule_once(partial(self.ids.board.press_button,
                                        move[1], is_engine_move=True, engine_move=engine_move), 1)
        else:
            Logger.info("Waiting for opponent to make a move")
            Clock.schedule_once(self.await_turn, 2)

    def setup_netgame(self):
        if not self.game_instance.my_turn:
            Logger.info("Waiting for opponent to make a move")
            self.movebox_moves = "Tegenstander aan zet"
            self.update_moves_list()
            Clock.schedule_once(self.await_turn, 5)
        else:
            self.movebox_moves = "Zelf aan zet!"
            self.update_moves_list()

    def turn(self, *args):
        """Return which side is to play w or b."""
        return str(board.fen).split()[5]

    def chesscell_clicked(self, id, *args):
        if self.game_instance.my_turn:
            if id == self.selected_square:
                self.update_board()
            elif self.selected_square is None:
                self.select_piece(id)
            else:
                self.move_piece(id)

    def overview_clicked(self, id, *args):
        Clock.unschedule(self.await_turn)
        app = App.get_running_app()
        app.manager.current = 'overview'
        app.manager.get_screen('overview').get_current_games()

    def white_time_counter(self, *args, start=False, time=50, cancel=False):
        if start:
            self.white_time = str(time)
            global w_counter
            w_counter = Clock.schedule_interval(self.white_time_counter,
                                                self.interval)
        elif cancel:
            w_counter.cancel()
        else:
            self.white_time = str(round(float(self.white_time)
                                        - self.interval, 2))

    def black_time_counter(self, *args, start=False, time=50, cancel=False):
        if start:
            self.black_time = str(time)
            global b_counter
            b_counter = Clock.schedule_interval(self.black_time_counter,
                                                self.interval)
        elif cancel:
            b_counter.cancel()
        else:
            self.black_time = str(round(float(self.black_time)
                                        - self.interval, 2))

    def setup_clocks(self, *args, time=60, interval=0.1):
        pass
        # self.black_time = str(time)
        # self.white_time = str(time)
        # self.interval = interval

    def end_game(self, reason, *args):
        # Clock.schedule_once(partial(self.white_time_counter, cancel=True), 1)
        # Clock.schedule_once(partial(self.black_time_counter, cancel=True), 1)
        self.movebox_moves = f"Game over! {reason}\n\n"
        self.update_moves_list()
        print(reason)
        self.movebox_moves += "\n\n"
        if 'white' in reason:
            self.movebox_moves += 'Black won'
        elif 'black' in reason:
            self.movebox_moves += 'White won'
        else:
            if board.result()[-1] == '1':
                self.movebox_moves += 'Black won'
            elif board.result()[0] == '1':
                self.movebox_moves += 'White won'
            else:
                self.movebox_moves += 'Draw'

    def game_end_check(self, *args):
        if board.is_game_over():
            if board.is_checkmate():
                self.end_game('checkmate')
            elif board.is_stalemate():
                self.end_game('stalemate')
            elif board.is_insufficient_material():
                self.end_game('insufficient_material')
            elif board.is_seventyfive_moves():
                self.end_game('seventy five moves')
            elif board.is_fivefold_repetition():
                self.end_game('fivefold_repetition')
            return True

        # elif float(self.white_time) < 0:
        #     self.end_game('white ran out of time')
        #     return True
        # elif float(self.black_time) < 0:
        #     self.end_game('black ran out of time')
        #     return True

        return False


class GameScreen(Screen):
    game_instance = ObjectProperty(None)

    def load_game(self):
        # Loading game
        Logger.info("Loading game...")
        chess_game = self.children[0]
        chess_game.game_instance = self.game_instance
        global board
        board = self.game_instance.board
        if self.game_instance.my_side == "White":
            chess_game.black_time = "Tegenstander"
            chess_game.white_time = "Ik zelf"
        else:
            chess_game.black_time = "Ik zelf"
            chess_game.white_time = "Tegenstander"

        chess_game.update_board()  # self.game_instance.board)
        chess_game.setup_netgame()
        # chess_game.setup_clocks(time=60, interval=.01)


class ChessboardApp(App):
    username = StringProperty(None)
    password = StringProperty(None)
    player = ObjectProperty(None)
    manager = ObjectProperty(None)

    def check_background_games(self, *args):
        """Check if there are changes to any current games for this player."""
        if self.username is None or self.password is None:
            return
        if self.player.logged_in is False:
            return

        before_load = list(self.player.current_games)
        self.player.load_games_from_server()
        after_load = list(self.player.current_games)
        new_games = [game for game in after_load if game not in before_load]
        removed_games = [game for game in before_load if game not in after_load]

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
