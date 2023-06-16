import tekore as tk
import sys
from io import StringIO
import random
import string
import webbrowser

auth = None


def open_browser_login(conf):
    global auth
    try:
        cred = tk.Credentials(*conf)
        auth = tk.UserAuth(cred, tk.scope.user_read_playback_state)
        print(auth)
        webbrowser.open(auth.url)
    except Exception as e:
        print(str(e))
        pass


def get_token(callback):
    token = None

    if auth:
        try:
            code = tk.parse_code_from_url(callback)
            token = auth.request_token(code, auth.state)
        except Exception as e:
            print(str(e))
            # Token invalid
            pass

    return token


def try_get_spotify_session_from_file(file):
    spotify = None
    user_spotify = None

    try:
        # Try to get token from file
        conf_user = tk.config_from_file(file, return_refresh=True)
        user_token = tk.refresh_user_token(*conf_user[:2], conf_user[3])
        app_token = tk.request_client_token(conf_user[0], conf_user[1])
        spotify = tk.Spotify(app_token)
        user_spotify = tk.Spotify(user_token, asynchronous=True)
    except:
        pass

    return spotify, user_spotify


def try_get_spotify_session(user_token, conf, file):
    spotify = None
    user_spotify = None

    try:
        # App Token
        app_token = tk.request_client_token(conf[0], conf[1])
        spotify = tk.Spotify(app_token)

        # User token
        test_user_spotify = tk.Spotify(user_token, asynchronous=False)
        user_profile = test_user_spotify.current_user()

        # If not error
        user_spotify = tk.Spotify(user_token, asynchronous=True)
        tk.config_to_file(file, conf + (user_token.refresh_token,))
    except:
        pass

    return spotify, user_spotify

