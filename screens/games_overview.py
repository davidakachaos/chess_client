from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from screens.queue_for_game import QueueForGame


class GameRow(BoxLayout):
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        # self.width = 300
        self.size_hint_y = None
        self.height = 50
        self.game = game
        game_description = f"Spel versus {game.my_opponent}."
        if game.over:
            game_description += f"\nAfgelopen! Resultaat: {game.over_reason}"
        else:
            if game.my_turn:
                game_description += " Mijn zet!"
            else:
                game_description += " Tegenstander aan zet."
        # Label for game
        game_label = Label(text=game_description)
        game_label.halign = 'left'
        game_label.valign = 'top'
        game_label.padding = [10, 10]
        # game_label.size = game_label.texture_size

        self.add_widget(game_label)
        # Play button, beside label
        play_button = Button(text="Naar spel")
        play_button.size_hint = 0.2, 1
        play_button.bind(on_press=self.goto_game)
        self.add_widget(play_button)

    def goto_game(self, _):
        Logger.info(f"Game {self.game.guid} openen")
        app = App.get_running_app()
        game_screen = app.manager.get_screen('game')
        game_screen.game_instance = self.game
        app.manager.current = 'game'
        game_screen.load_game()


class GamesOverview(Screen):
    """The screen with current games for a player."""

    current_games = ObjectProperty(None)

    def get_current_games(self):
        self.ids.current_games.clear_widgets()
        app = App.get_running_app()
        current = app.player.current_games
        done = app.player.done_games
        Logger.info(f"Found {len(current + done)} games for player")
        for game in done:
            self.ids.done_games.add_widget(GameRow(game))
        for game in current:
            self.ids.current_games.add_widget(GameRow(game))

    def queue_new_random_game(self):
        app = App.get_running_app()
        app.manager.add_widget(QueueForGame(name="queue"))
        app.manager.current = "queue"
        Clock.schedule_once(app.manager.get_screen("queue").start_queue_up, 0.3)
