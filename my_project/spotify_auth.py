import datetime
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth  # Corrected import
from flask import Flask, redirect, request, jsonify, session
import logging

app = Flask(__name__)
app.secret_key = 'Ezenagu101#'

CLIENT_ID = '20f9abbba2dd46868feb34d3111352f0'
CLIENT_SECRET_ID = 'dbdc5330d9bf4cd591ea9c56cc646d87'
REDIRECT_URI = 'http://localhost:5000/callback'

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def home():
    return """
    <h1>Welcome to AudioAlly</h1>
    <a href='/login'>Login with Spotify</a>
    <form action="/create_recommendation_playlist" method="post" style="margin-top: 20px;">
        <div>
            <label for="artists">Favorite Artists (comma separated):</label>
            <input type="text" id="artists" name="artists" required>
        </div>
        <div>
            <label for="genres">Favorite Genres (comma separated):</label>
            <input type="text" id="genres" name="genres" required>
        </div>
        <div>
            <label for="location">Geographic Location:</label>
            <input type="text" id="location" name="location" required>
        </div>
        <div>
            <label for="trends">Current Trends (comma separated track IDs, optional):</label>
            <input type="text" id="trends" name="trends">
        </div>
        <button type="submit">Create Personalized Playlist</button>
    </form>
    """

@app.route('/login')
def login():
    scope = 'playlist-modify-public'
    sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET_ID, redirect_uri=REDIRECT_URI, scope=scope)
    auth_url = sp_oauth.get_authorize_url()
    logging.debug(f"Redirecting to Spotify auth URL: {auth_url}")
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET_ID, redirect_uri=REDIRECT_URI)
        token_info = sp_oauth.get_access_token(code)
        if token_info:
            session['access_token'] = token_info['access_token']
            session['expires_at'] = token_info['expires_at']
            return redirect('/create_recommendation_playlist')
        else:
            return jsonify({"error": "Failed to retrieve access token."}), 400
    else:
        return jsonify({"error": "Authorization code not found."}), 400

def create_spotify_client():
    access_token = session.get('access_token')
    if access_token:
        return spotipy.Spotify(auth=access_token)
    else:
        return None
    

# @app.route('/create_recommendation_playlist', methods=['POST', 'GET'])
# def create_recommendation_playlist():
#     if request.method == 'POST':
#         sp = create_spotify_client()
#         if sp:
#             favorite_artists = request.form.get('artists')
#             favorite_genres = request.form.get('genres')
#             location = request.form.get('location')
#             trends = get_recent_tracks(sp, location)  # Fetch recent tracks as trends

#             # Ensure form data exists before attempting to split
#             if favorite_artists:
#                 favorite_artists = favorite_artists.split(',')
#             else:
#                 # Handle missing 'artists' form data (e.g., set default value or return error response)
#                 return jsonify({"error": "'artists' form data is missing."}), 400

#             if favorite_genres:
#                 favorite_genres = favorite_genres.split(',')
#             else:
#                 # Handle missing 'genres' form data (e.g., set default value or return error response)
#                 return jsonify({"error": "'genres' form data is missing."}), 400

#             if location:
#                 # Use the Spotify API to get recommendations based on user preferences and trends
#                 recommendations = get_recommendations(sp, favorite_artists, favorite_genres, location, trends)

#                 if recommendations:
#                     # Create a new playlist using the Spotify API
#                     playlist_name = "Your Personalized Playlist"
#                     playlist_description = "Created based on your favorite artists, genres, and current trends."
#                     user_info = sp.current_user()
#                     user_id = user_info['id']
#                     playlist_response = sp.user_playlist_create(user_id, name=playlist_name, public=True, description=playlist_description)
                    
#                     if playlist_response:
#                         playlist_id = playlist_response['id']
#                         # Add tracks to the playlist
#                         add_tracks_response = sp.user_playlist_add_tracks(user_id, playlist_id, recommendations)
#                         if add_tracks_response:
#                             return jsonify({"message": "Playlist created successfully!", "playlist_id": playlist_id})
#                         else:
#                             return jsonify({"error": "Failed to add tracks to the playlist."})
#                     else:
#                         return jsonify({"error": "Failed to create playlist."})
#                 else:
#                     return jsonify({"error": "Failed to get recommendations."})
#             else:
#                 # Handle missing 'location' form data (e.g., set default value or return error response)
#                 return jsonify({"error": "'location' form data is missing."}), 400
#         else:
#             return redirect('/login')
#     elif request.method == 'GET':
#         # Handle GET request method (if needed)
#         return jsonify({"message": "GET request received."})



@app.route('/create_recommendation_playlist', methods=['POST', 'GET'])
def create_recommendation_playlist():
    print(request.form)
    sp = create_spotify_client()
    if sp:
        favorite_artists = request.form.get('artists').split(',')
        favorite_genres = request.form.get('genres').split(',')
        location = request.form.get('location')
        trends = get_recent_tracks(sp, location)  # Fetch recent tracks as trends

        # Use the Spotify API to get recommendations based on user preferences and trends
        recommendations = get_recommendations(sp, favorite_artists, favorite_genres, location, trends)

        if recommendations:
            # Create a new playlist using the Spotify API
            playlist_name = "Your Personalized Playlist"
            playlist_description = "Created based on your favorite artists, genres, and current trends."
            user_info = sp.current_user()
            user_id = user_info['id']
            playlist_response = sp.user_playlist_create(user_id, name=playlist_name, public=True, description=playlist_description)
            
            if playlist_response:
                playlist_id = playlist_response['id']
                # Add tracks to the playlist
                add_tracks_response = sp.user_playlist_add_tracks(user_id, playlist_id, recommendations)
                if add_tracks_response:
                    return jsonify({"message": "Playlist created successfully!", "playlist_id": playlist_id})
                else:
                    return jsonify({"error": "Failed to add tracks to the playlist."})
            else:
                return jsonify({"error": "Failed to create playlist."})
        else:
            return jsonify({"error": "Failed to get recommendations."})
    else:
        return redirect('/login')

def get_recent_tracks(sp, country):
    # Get current date
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')

    # Calculate date 2 years ago
    two_years_ago = (datetime.datetime.now() - datetime.timedelta(days=365 * 2)).strftime('%Y-%m-%d')

    # Search for tracks released within the last 2 years
    results = sp.search(q=f'release_date:{two_years_ago}:{current_date}', type='track', market=country, limit=10)

    if results and 'tracks' in results:
        track_ids = [track['id'] for track in results['tracks']['items']]
        return track_ids
    else:
        return None

def get_recommendations(sp, seed_artists, seed_genres, country, trends):
    # Get recommendations from Spotify API
    recommendations = sp.recommendations(seed_artists=seed_artists, seed_genres=seed_genres, seed_tracks=trends, country=country, limit=20)
    
    if recommendations:
        track_ids = [track['id'] for track in recommendations['tracks']]
        return track_ids
    else:
        return None
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)