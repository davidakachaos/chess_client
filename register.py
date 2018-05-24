from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, FallOutTransition
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

from models.player import Player


class Register(Screen):

    def __init__(self, name=None, *args):
        super(Register, self).__init__(name=name, *args)
        Logger.info("Loading registration screen")
        Clock.schedule_once(self._setup_boxes, 0)

    def _setup_boxes(self, _):
        Logger.debug('Setting boxes')
        if len(self.ids) == 0:
            return
        self.ids.login.write_tab = False
        self.ids.login.focus = True
        self.ids.password.write_tab = False
        self.ids.password_confirm.write_tab = False
        self.ids.login.bind(on_text_validate=self.on_enter)
        self.ids.password.bind(on_text_validate=self.on_enter)
        self.ids.password_confirm.bind(on_text_validate=self.on_enter)

    def on_enter(self, *instance):
        """Enter in a textfield triggers registration."""
        if instance:
            self.do_register()

    def do_register(self):
        app = App.get_running_app()

        if len(self.ids.login.text) == 0:
            self.register_failed_message(message="Vul een gebruikersnaam in!")
            return False

        if len(self.ids.password.text) == 0 or len(self.ids.password_confirm.text) == 0:
            self.register_failed_message(message="Vul een wachtwoord in!")
            return False

        Logger.info(f"Trying: {self.ids.login.text}/{self.ids.password.text}")
        app.player = Player(self.ids.login.text)
        app.player.password = self.ids.password.text
        register_result = app.player.register(self.ids.password_confirm.text)

        if register_result == "username_taken":
            self.register_failed_message(
                message="Gebruikersnaam al in gebruik!")
            app.player = None
            return False

        if register_result == "invalid_password":
            self.register_failed_message(message="Wachtwoord ongeldig!")
            app.player = None
            return False

        if register_result == "register_failed!":
            self.register_failed_message(
                message="Onverwachte fout bij registratie!")
            app.player = None
            return False

        if app.player.logged_in:
            self.manager.transition = FallOutTransition()
            self.manager.current = 'overview'
            self.manager.get_screen('overview').get_current_games()

            app.config.read(app.get_application_config())
            app.config.write()

    def register_failed_message(self, message=""):
        self.resetForm()
        self.ids.login.focus = True

        layout = GridLayout(cols=1, padding=10)
        popupLabel = Label(text=f"Registeren mislukt!\n{message}")
        closeButton = Button(text="Okay")

        layout.add_widget(popupLabel)
        layout.add_widget(closeButton)

        # Instantiate the modal popup and display
        popup = Popup(title='Registeren mislukt!',
                      content=layout)
        popup.bind(on_dismiss=self.refocus)
        popup.open()
        # Attach close button press with popup.dismiss action
        closeButton.bind(on_press=popup.dismiss)

    def refocus(self, _):
        Clock.schedule_once(self._setup_boxes, 0.3)

    def resetForm(self):
        self.ids.login.text = ""
        self.ids.password.text = ""
        self.ids.password_confirm.text = ""
