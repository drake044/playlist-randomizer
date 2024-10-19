import os
import random
import time

import spotipy
from colorama import Fore, Style, init
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

# Load environment variables from .env file
load_dotenv()

# Spotify API credentials from environment variables
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Spotify API connection
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-read-private playlist-modify-private user-library-read"
))


def fetch_playlists():
    """Fetch user's playlists."""
    playlists = sp.current_user_playlists()
    playlist_list = []
    while playlists:
        playlist_list.extend(playlists['items'])
        playlists = sp.next(playlists) if playlists['next'] else None
    return playlist_list


def fetch_tracks(playlist_id):
    """Fetch tracks from a playlist with a progress bar."""
    results = sp.playlist_tracks(playlist_id)
    total_tracks = results['total']
    tracks = results['items']

    print("\nFetching tracks:")
    with tqdm(total=total_tracks, desc="Progress", ncols=100) as pbar:
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
            pbar.update(len(results['items']))
        pbar.update(total_tracks - len(tracks))

    return tracks


def fetch_genres(track_id):
    """Fetch genres based on a track's artist."""
    track = sp.track(track_id)
    artist_id = track['album']['artists'][0]['id']
    artist = sp.artist(artist_id)
    return artist.get('genres', [])


def display_tracks_with_genres(tracks):
    """Display tracks with their genres."""
    for idx, track in enumerate(tracks, start=1):
        track_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        track_genres = fetch_genres(track['track']['id'])
        print(f"{Fore.GREEN}{idx}. {track_name} by {artist_name} {Fore.YELLOW}[Genres: {', '.join(track_genres)}]")


def randomize_with_genres(tracks):
    #Randomize tracks along with genre-based recommendations
    genres_set = set()
    print("\nFetching genres and recommendations for similar tracks...")

    with tqdm(total=len(tracks), desc="Progress", ncols=100) as pbar:
        for track in tracks:
            genres = fetch_genres(track['track']['id'])
            genres_set.update(genres)
            pbar.update(1)

    all_tracks = tracks.copy()
    print("\nFetching recommendations based on genres...")

    with tqdm(total=len(genres_set), desc="Fetching Recommended Tracks", ncols=100) as pbar:
        for genre in genres_set:
            recommendations = sp.recommendations(seed_genres=[genre], limit=5)
            for rec_track in recommendations['tracks']:
                all_tracks.append({'track': rec_track})
            pbar.update(1)

    random.shuffle(all_tracks)
    return all_tracks


def add_tracks_to_playlist(playlist_id, tracks):
    """Add tracks to a playlist with a progress bar."""
    track_uris = [track['track']['uri'] for track in tracks]

    print("\nAdding tracks to the new playlist:")
    with tqdm(total=len(track_uris), desc="Adding Tracks", ncols=100) as pbar:
        for i in range(0, len(track_uris), 100):
            sp.playlist_add_items(playlist_id, track_uris[i:i+100])
            pbar.update(min(100, len(track_uris) - i))


def simulate_playlist_creation_progress():
    """Simulate progress bar for playlist creation."""
    print("\nCreating new playlist...")
    with tqdm(total=100, desc="Creating Playlist", ncols=100) as pbar:
        for _ in range(5):
            time.sleep(0.3)
            pbar.update(20)


def create_playlist(name):
    """Create a new playlist."""
    user_id = sp.current_user()['id']
    simulate_playlist_creation_progress()
    new_playlist = sp.user_playlist_create(user_id, name, public=False)
    return new_playlist['id']


def main():
    """Main function to run the playlist randomizer."""
    print("Fetching your playlists...")
    playlists = fetch_playlists()
    for idx, playlist in enumerate(playlists, start=1):
        print(f"{idx}. {playlist['name']}")

    while True:
        try:
            playlist_choice = int(input("Enter the number of the playlist you want to randomize: ")) - 1
            if 0 <= playlist_choice < len(playlists):
                break
            else:
                print(f"Please enter a number between 1 and {len(playlists)}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

    selected_playlist = playlists[playlist_choice]
    playlist_id = selected_playlist['id']

    print(f"Fetching tracks from playlist: {selected_playlist['name']}...")
    tracks = fetch_tracks(playlist_id)
    print(f"Fetched {len(tracks)} tracks.")

    print("\nTracks and their genres:")
    display_tracks_with_genres(tracks)

    while True:
        use_genre_based_randomization = input("\nDo you want to randomize and include tracks from similar genres? (yes/no): ").lower()
        if use_genre_based_randomization in ['yes', 'no']:
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    if use_genre_based_randomization == 'yes':
        randomized_tracks = randomize_with_genres(tracks)
    else:
        random.shuffle(tracks)
        randomized_tracks = tracks

    print("\nRandomized Playlist:")
    print("--------------------")
    for idx, track in enumerate(randomized_tracks, start=1):
        print(f"{idx}. {track['track']['name']} by {track['track']['artists'][0]['name']}")

    while True:
        create_new_playlist = input("\nWould you like to create a new playlist with these tracks? (yes/no): ").lower()
        if create_new_playlist in ['yes', 'no']:
            break
        else:
            print("Invalid input. Please enter 'yes' or 'no'.")

    if create_new_playlist == 'yes':
        new_playlist_name = input("Enter the name for the new playlist: ")
        new_playlist_id = create_playlist(new_playlist_name)
        add_tracks_to_playlist(new_playlist_id, randomized_tracks)
        print(f"New playlist '{new_playlist_name}' created successfully!")


if __name__ == "__main__":
    main()
