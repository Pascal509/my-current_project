import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# from dotenv import load_dotenv
import os
import sys
import json
import webbrowser
from spotipy.oauth2 import SpotifyOAuth
from json.decoder import JSONDecodeError
from spotipy.exceptions import SpotifyException

username = sys.argv[1]

# 31t3wzqxii6bwmmsdffqd7tbwgku
scope = "user-library-read"

try:
    sp_oauth=SpotifyOAuth(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    redirect_url=os.getenv("REDIRECT_URI"),
    scope=scope,
    username=username
    )
    
    token_info = sp_oauth.get_cached_token()

    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        print(f"Please navigate here: {auth_url}")
        response = input("Paste the redirect-URL here: ")
        code = sp_oauth.parse_response_code(response)
        token_info = sp_oauth.get_access_token(code)

    token = token_info['access_token']
    spotifyObject = spotipy.Spotify(auth=token)

    results = spotifyObject.current_user_saved_tracks()
    for idx, item in enumerate(results['items']):
        track = item['track']
        print(idx, track['artiste'])

except SpotifyException as e:
    print(f"Spotify exception: {e}")
    cache_file = f".cache-{username}"
    if os.path.exists(cache_file):
        os.remove(cache_file)
    

# Crete spotify object
spotifyObject = spotipy.Spotify(auth=token)

# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

# results = sp.current_user_saved_tracks()

# for idx, item in enumerate(results['items']):
#     track = item['track']
#     print(idx, track['artists'][0]['name'])