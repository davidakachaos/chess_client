from kivy.app import App
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, FallOutTransition
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout

from models.player import Player


class Login(Screen):

    def __init__(self, name=None, *args):
        super(Login, self).__init__(name=name, *args)
        Clock.schedule_once(self._setup_boxes, 0)

    def _setup_boxes(self, _):
        Logger.debug('Setting boxes')
        self.ids.login.write_tab = False
        self.ids.login.focus = True
        self.ids.password.write_tab = False
        self.ids.login.bind(on_text_validate=self.on_enter)
        self.ids.password.bind(on_text_validate=self.on_enter)

    def on_enter(self, *instance):
        if instance:
            self.do_login(self.ids['login'].text, self.ids['password'].text)

    def do_login(self, loginText, passwordText):
        app = App.get_running_app()

        app.username = loginText
        app.password = passwordText

        if len(loginText) == 0 or len(passwordText) == 0:
            self.ids.login.focus = True
            return False

        Logger.info(f"Trying: {loginText}/{passwordText}")
        app.player = Player(loginText, password=passwordText)

        if app.player.logged_in:
            self.manager.transition = FallOutTransition()
            self.manager.current = 'overview'
            self.manager.get_screen('overview').get_current_games()

            app.config.read(app.get_application_config())
            app.config.write()
        else:
            self.resetForm()
            self.ids.login.focus = True
            self.loginFailedMessage()

    def loginFailedMessage(self):
        layout = GridLayout(cols=1, padding=10)
        popupLabel = Label(text="Login failed!")
        closeButton = Button(text="Okay")

        layout.add_widget(popupLabel)
        layout.add_widget(closeButton)

        # Instantiate the modal popup and display
        popup = Popup(title='Login failed',
                      content=layout)
        popup.bind(on_dismiss=self.refocus)
        popup.open()
        # Attach close button press with popup.dismiss action
        closeButton.bind(on_press=popup.dismiss)

    def refocus(self, _):
        Clock.schedule_once(self._setup_boxes, 0.3)

    def resetForm(self):
        self.ids['login'].text = ""
        self.ids['password'].text = ""
