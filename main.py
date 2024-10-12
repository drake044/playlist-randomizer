import os
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Spotify API credentials
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# Spotify OAuth setup
scope = "playlist-read-private playlist-modify-private playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=scope
))

def get_user_playlists():
    """Fetch all user playlists."""
    results = sp.current_user_playlists()
    playlists = results['items']
    return playlists

def display_playlists(playlists):
    """Display playlists and their IDs."""
    for idx, playlist in enumerate(playlists):
        print(f"{idx + 1}: {playlist['name']} (ID: {playlist['id']})")

def get_playlist_tracks(playlist_id):
    """Fetch tracks from the playlist."""
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    return tracks

def shuffle_tracks(tracks):
    """Shuffle the tracks."""
    random.shuffle(tracks)
    return tracks

def create_new_playlist(name, description):
    """Create a new playlist for the user."""
    user_id = sp.current_user()['id']
    new_playlist = sp.user_playlist_create(user_id, name, description=description)
    return new_playlist['id']

def add_tracks_to_playlist(playlist_id, tracks):
    """Add shuffled tracks to the new playlist."""
    track_ids = [track['track']['id'] for track in tracks]
    sp.playlist_add_items(playlist_id, track_ids)

def main():
    print("Fetching your playlists...")
    playlists = get_user_playlists()
    
    if not playlists:
        print("No playlists found.")
        return
    
    display_playlists(playlists)
    
    playlist_index = int(input("Enter the number of the playlist you want to shuffle: ")) - 1
    selected_playlist = playlists[playlist_index]
    playlist_id = selected_playlist['id']
    print(f"Selected playlist: {selected_playlist['name']}")
    
    # Fetch tracks from the selected playlist
    tracks = get_playlist_tracks(playlist_id)
    
    if not tracks:
        print("No tracks found in this playlist.")
        return
    
    # Shuffle tracks
    shuffled_tracks = shuffle_tracks(tracks)
    print(f"Shuffling {len(tracks)} tracks...")
    
    # Create a new randomized playlist
    new_playlist_name = f"Shuffled - {selected_playlist['name']}"
    new_playlist_description = f"A shuffled version of {selected_playlist['name']}"
    new_playlist_id = create_new_playlist(new_playlist_name, new_playlist_description)
    
    # Add shuffled tracks to the new playlist
    add_tracks_to_playlist(new_playlist_id, shuffled_tracks)
    print(f"New playlist created: {new_playlist_name}")

if __name__ == '__main__':
    main()
