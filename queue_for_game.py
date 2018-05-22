"""Manages the Screen for queuing for games."""
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty
from models.player import Player
from models.game import Game
import threading


class QueueForGame(Screen):
    """A screen for queuing for a new game."""

    stop = threading.Event()

    def start_queue_up(self):
        threading.Thread(target=self.queue_up).start()

    def queue_up(self):
        app = App.get_running_app()
        try:
            self.update_label_text("In de wachtrij voor een nieuw spel")
        except Exception as e:
            return False

        # This blocks the thread!!
        new_game_id = app.player.net.queue_up_new_game()
        game = Game(new_game_id, app.player.net)
        self.update_label_text(f"Nieuw spel tegen {game.my_opponent} gestart!")

    @mainthread
    def update_label_text(self, new_text):
        self.ids.wachtrijstatus.text = f"Wachtrij Status:\n\n{new_text}"


# Fake app to test layout
class QueueApp(App):  # noqa: D101
    player = ObjectProperty(None)

    def build(self):  # noqa: D102
        manager = ScreenManager()
        manager.add_widget(QueueForGame(name='queue'))
        manager.current = "queue"
        app = App.get_running_app()
        app.player = Player("David2", "Welkom123")
        return manager


if __name__ == '__main__':
    QueueApp().run()
