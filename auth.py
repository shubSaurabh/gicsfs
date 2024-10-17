# auth.py
import webbrowser
import requests
from requests_oauthlib import OAuth2Session
import logging

class GitHubAuth:
    AUTH_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    REDIRECT_URI = "https://localhost"  # Use https as github does not allow http
    
    SCOPE = "read:user,repo" 

    def __init__(self, client_id, client_secret, logger=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = None
        self.logger = logger or logging.getLogger("SecureFileStorage")

    def authenticate(self):
        """Authenticate the user using GitHub OAuth."""
        try:
            # Pass the scope as a space-separated string
            oauth = OAuth2Session(self.client_id, redirect_uri=self.REDIRECT_URI, scope=self.SCOPE.split())
            auth_url, state = oauth.authorization_url(self.AUTH_URL)
            print(f"Please go to {auth_url} and authorize access.")
            webbrowser.open(auth_url)

            # GitHub returns a URL with the authorization code after login
            redirect_response = input("Paste the full redirect URL here, https://localhost/?code=<code>&state=<state>: ")
            token = oauth.fetch_token(self.TOKEN_URL, client_secret=self.client_secret, authorization_response=redirect_response)
            self.session = oauth
            self.logger.info("OAuth2 authentication successful.")
            return token["access_token"]
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            raise
