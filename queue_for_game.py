"""Manages the Screen for queuing for games."""
from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.logger import Logger
from kivy.clock import mainthread
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import ObjectProperty
from models.player import Player
from models.game import Game
import threading
from datetime import datetime
from time import sleep


class QueueForGame(Screen):
    """A screen for queuing for a new game."""

    stop = threading.Event()

    def start_queue_up(self, *args):
        """Spawns a thread to queue for a new game."""
        # Reset the flag if needed.
        self.stop.clear()
        threading.Thread(target=self.queue_up).start()

    def queue_up(self):
        app = App.get_running_app()
        self.update_label_text("In de wachtrij voor een nieuw spel")
        start_q = datetime.now()
        new_game_id = app.player.net.queue_up_new_game(blocking=False)
        while new_game_id == "queued_for_game":
            tim = datetime.now()
            seconds_in_q = int((tim - start_q).total_seconds())
            self.update_label_text(f"In de wachtrij voor een nieuw spel.\nTijd in wachtrij: {seconds_in_q}")
            sleep(1)
            if self.stop.is_set():
                # Need to de-queue?
                self.update_label_text(f"Wachtrij verlaten!\nTijd in wachtrij: {seconds_in_q}")
                return
            else:
                new_game_id = app.player.net.queue_up_new_game(blocking=False)

        game = Game(new_game_id, app.player.net)
        self.update_label_text(f"Nieuw spel tegen {game.my_opponent} gestart!")
        sleep(2)
        game_screen = app.manager.get_screen('game')
        game_screen.game_instance = game
        app.manager.current = 'game'
        game_screen.load_game()

    def dequeue(self):
        app = App.get_running_app()
        self.stop.set()
        dequeue_res = app.player.net.dequeue()
        if dequeue_res == "dequeued":
            Logger.info("Successvol uit wachtrij gegaan.")
        else:
            Logger.info("Stond niet in wachtrij!")

        # Switch back to the overview screen.
        sleep(2)
        app.manager.current = "overview"


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
