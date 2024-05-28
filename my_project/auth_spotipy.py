import os
from flask import Flask, redirect, session, request
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = os.urandom(24)

sp_oauth = SpotifyOAuth(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:5000/callback",
    scope="user-read-private user-read-email playlist-read-private playlist-read-collaborative playlist-modify-public",
)

@app.route("/")
def index():
    return "<a href='/login'>Login with Spotify</a>"

@app.route("/login")
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect("/playlists")

@app.route("/playlists")
def playlists():
    token_info = session.get("token_info")
    if not token_info:
        return redirect("/login")

    access_token = token_info["access_token"]
    # Use access_token to make requests to Spotify API
    return "You are authenticated. Now you can access user's playlists."

if __name__ == "__main__":
    app.run(debug=True)
