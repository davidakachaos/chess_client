"""The login screen module."""
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
    """The login screen.

    Parameters
    ----------
    name : String
        The name of this screen as the screen manager can access.

    """

    def __init__(self, name=None, *args):  # noqa: D107
        super(Login, self).__init__(name=name, *args)
        Clock.schedule_once(self._setup_boxes, 0)

    def _setup_boxes(self, _):
        """Set the textboxes properties on load."""
        Logger.debug('Setting boxes')
        self.ids.login.write_tab = False
        self.ids.login.focus = True
        self.ids.password.write_tab = False
        self.ids.login.bind(on_text_validate=self.on_enter)
        self.ids.password.bind(on_text_validate=self.on_enter)

    def on_enter(self, *instance):
        """Login when user hits enter in a textbox."""
        if instance:
            self.do_login(self.ids['login'].text, self.ids['password'].text)

    def do_login(self, loginText, passwordText):
        """Login to the server with login and password.

        Parameters
        ----------
        loginText : String
            The username to login with.
        passwordText : String
            The unhashed password to try the login with.

        Returns
        -------
        If login is sucessful, proceed to the application.
        Else show a popup and clear the textboxes.

        """
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

    def goto_register(self):
        """Change to the register account screen."""
        self.manager.transition = FallOutTransition()
        self.manager.current = "registration"

    def loginFailedMessage(self):
        """Show a login failed message to the user."""
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
        """Schedual a call to refocus the login textbox."""
        Clock.schedule_once(self._setup_boxes, 0.3)

    def resetForm(self):
        """Reset the textboxes to empty."""
        self.ids['login'].text = ""
        self.ids['password'].text = ""
