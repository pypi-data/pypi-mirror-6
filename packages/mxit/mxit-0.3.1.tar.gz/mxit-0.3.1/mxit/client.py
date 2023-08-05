from mxit.oauth import OAuth
from mxit.services import MessagingService, UserService


class Mxit():
    """
    Mxit API wrapper
    """

    def __init__(self, client_id, client_secret, redirect_uri=None, state=None, cache=None):

        # Auth
        self.oauth = OAuth(client_id, client_secret, redirect_uri, state, cache)

        # Services
        self.messaging = MessagingService(self.oauth)
        self.users = UserService(self.oauth)