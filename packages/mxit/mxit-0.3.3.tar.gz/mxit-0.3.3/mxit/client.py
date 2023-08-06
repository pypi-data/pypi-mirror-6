from mxit.oauth import OAuth
from mxit.services import MessagingService, UserService


class Mxit():
    """
    Mxit API wrapper
    """

    def __init__(self, client_id, client_secret, redirect_uri=None, state=None, cache=None, verify_cert=True):

        # Auth
        self.oauth = OAuth(client_id, client_secret, redirect_uri, state, cache, verify_cert)

        # Services
        self.messaging = MessagingService(self.oauth)
        self.users = UserService(self.oauth)