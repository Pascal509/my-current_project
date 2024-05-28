import spotipy
import os
from dotenv import load_dotenv
from pathlib import Path
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List
from song_model import Song
from db import create_tables
from song_dao import get_all_songs, save_songs

my_project = Path(__file__).resolve().parent.parent

dotenv_path = my_project / '.env'

# Load the .env file
load_dotenv(dotenv_path)

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("SECRET_ID")


client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id,
    client_secret=client_secret
)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def search_songs(query: str) -> List[Song]:
    results = sp.search(query, limit=3)

    songs=[]
    for track in results["tracks"] ["items"]:
        song = Song(
            title=track["name"],
            artist=track["artists"][0]["name"],
            album=track["album"]["name"],
            spotify_id=track["id"]            
        )
        songs.append(song)

    return songs


if __name__ == '__main__':
    create_tables()

    while True:
        selection = input('''
            Enter:
                s - to search
                g - to print all songs in the db
                q - to quit
''')
        selection = selection.lower()

        if selection == 'q':
            break
        elif selection == 'g':
            print("All songs in the database: ")
            all_songs = get_all_songs()
            for song in all_songs:
                print(f"Title: {song.title} Artist: {song.artist} Album: {song.album}")

        elif selection == 's':
            search_query = input("Enter your Search: ")
            songs = search_songs(search_query)
            # Check if yoou got songs back
            if len(songs) > 0:
                print(f"Songs in database: len(songs)")
                # iterate and arrange songs in order
                for i, song in enumerate(songs, start=1):
                    print(f"{i}: Title: {song.title} Artist: {song.artist}")

                # save songs that were returned 
                save_choice = input("Do you want to save these songs (y/n): ")
                if save_choice.lower() == 'y':
                    save_songs(songs)
                else:
                    print("Songs not saved")
            else:
                print("No songs were found for your search")

        