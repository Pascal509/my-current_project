from flask import Flask, render_template, request
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from json import load

app = Flask(__name__)

client_id='20f9abbba2dd46868feb34d3111352f0'
client_secret='dbdc5330d9bf4cd591ea9c56cc646d87'
redirect_uri = 'http://localhost:5000/callback'


scope = "playlist-modify-public"
auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope)
sp = spotipy.Spotify(auth_manager=auth_manager)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create_playlist', methods=['POST'])
def create_playlist():
    genre = request.form['genre'] # pop

    results = sp.search(q='genre:' + genre, type='track', limit=3) # genre:pop
    track_uris = [track['uri'] for track in results['tracks']['items']]
    

    user_id = '31iijgb6oajny2ryvhowvc2uqqxm'
    playlist = sp.user_playlist_create(user_id, f'Your {genre} Tracks', public=True) # dir()
    
    sp.playlist_add_items(playlist['id'], track_uris)
    # playlist_link = 'https://open.spotify.com/playlist/' + playlist['id']
    
    playlist_url = playlist['external_urls']['spotify'] # https://open.spotify.com/playlist/5zYSJmVWxXzmvi30hEecqz
    
    return f"Playlist created! The link is <a href='{playlist_url}'>here</a>"

if __name__ == '__main__':
    app.run(port=5001, debug=True)