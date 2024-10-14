import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import colorama
from colorama import Fore, Style
from dotenv import load_dotenv
from tqdm import tqdm
import os
import time  # Used for simulating progress

# Load environment variables from .env file
load_dotenv()

# Spotify API credentials from environment variables
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

colorama.init(autoreset=True)

# Spotify API connection
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="playlist-read-private playlist-modify-private user-library-read"
))

# Fetch user's playlists
def fetch_playlists():
    playlists = sp.current_user_playlists()
    playlist_list = []
    while playlists:
        for playlist in playlists['items']:
            playlist_list.append(playlist)
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    return playlist_list

# Fetch tracks from a playlist with progress bar
def fetch_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    total_tracks = results['total']
    tracks = results['items']
    
    # Add progress bar for fetching tracks
    print("\nFetching tracks:")
    with tqdm(total=total_tracks, desc="Progress", ncols=100) as pbar:
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
            pbar.update(len(results['items']))  # Update progress bar
        pbar.update(total_tracks - len(tracks))  # Ensure it finishes to 100%
    
    return tracks

# Fetch genres based on a track's artist
def fetch_genres(track_id):
    track = sp.track(track_id)
    artist_id = track['album']['artists'][0]['id']
    artist = sp.artist(artist_id)
    return artist.get('genres', [])

# Display tracks with genres
def display_tracks_with_genres(tracks):
    for idx, track in enumerate(tracks, start=1):
        track_name = track['track']['name']
        artist_name = track['track']['artists'][0]['name']
        track_genres = fetch_genres(track['track']['id'])
        
        # Display track and its genres
        print(f"{Fore.GREEN}{idx}. {track_name} by {artist_name} {Fore.YELLOW}[Genres: {', '.join(track_genres)}]")

# Randomize tracks along with genre-based recommendations (with progress bar)
def randomize_with_genres(tracks):
    # Collect genres from the tracks
    genres_set = set()
    print("\nFetching genres and recommendations for similar tracks...")
    
    # Add progress bar for genre collection and randomization
    with tqdm(total=len(tracks), desc="Progress", ncols=100) as pbar:
        for track in tracks:
            genres = fetch_genres(track['track']['id'])
            genres_set.update(genres)
            pbar.update(1)
    
    # Fetch recommendations based on these genres
    all_tracks = tracks.copy()  # Start with the existing tracks
    print("\nFetching recommendations based on genres...")
    
    # Add progress bar for fetching recommended tracks
    with tqdm(total=len(genres_set), desc="Fetching Recommended Tracks", ncols=100) as pbar:
        for genre in genres_set:
            recommendations = sp.recommendations(seed_genres=[genre], limit=5)
            for rec_track in recommendations['tracks']:
                all_tracks.append({
                    'track': rec_track  # Using the same structure as fetched tracks
                })
            pbar.update(1)
    
    # Shuffle all tracks (current playlist + recommended tracks)
    random.shuffle(all_tracks)
    return all_tracks

# Add tracks to a playlist with a progress bar
def add_tracks_to_playlist(playlist_id, tracks):
    track_uris = [track['track']['uri'] for track in tracks]
    
    # Add progress bar for adding tracks
    print("\nAdding tracks to the new playlist:")
    with tqdm(total=len(track_uris), desc="Adding Tracks", ncols=100) as pbar:
        # We add tracks in chunks of 100 as per Spotify's API limit
        for i in range(0, len(track_uris), 100):
            sp.playlist_add_items(playlist_id, track_uris[i:i+100])
            pbar.update(100 if len(track_uris) - i > 100 else len(track_uris) - i)

# Simulate progress bar for playlist creation
def simulate_playlist_creation_progress():
    print("\nCreating new playlist...")
    with tqdm(total=100, desc="Creating Playlist", ncols=100) as pbar:
        for _ in range(5):  # Simulate 5 steps of progress
            time.sleep(0.3)  # Simulating delay
            pbar.update(20)

# Create a new playlist
def create_playlist(name):
    user_id = sp.current_user()['id']
    
    # Simulate progress bar during playlist creation
    simulate_playlist_creation_progress()
    
    new_playlist = sp.user_playlist_create(user_id, name, public=False)
    return new_playlist['id']

def main():
    print("Fetching your playlists...")
    playlists = fetch_playlists()
    for idx, playlist in enumerate(playlists, start=1):
        print(f"{idx}. {playlist['name']}")
    
    playlist_choice = int(input("Enter the number of the playlist you want to randomize: ")) - 1
    selected_playlist = playlists[playlist_choice]
    playlist_id = selected_playlist['id']
    
    print(f"Fetching tracks from playlist: {selected_playlist['name']}...")
    tracks = fetch_tracks(playlist_id)
    print(f"Fetched {len(tracks)} tracks.")
    
    # Display tracks with genres
    print("\nTracks and their genres:")
    display_tracks_with_genres(tracks)

    # Ask the user if they want to randomize with genres
    use_genre_based_randomization = input("\nDo you want to randomize and include tracks from similar genres? (yes/no): ").lower()
    if use_genre_based_randomization == 'yes':
        randomized_tracks = randomize_with_genres(tracks)
    else:
        random.shuffle(tracks)
        randomized_tracks = tracks
    
    print("\nRandomized Playlist:")
    print("--------------------")
    for idx, track in enumerate(randomized_tracks, start=1):
        print(f"{idx}. {track['track']['name']} by {track['track']['artists'][0]['name']}")
    
    create_new_playlist = input("\nWould you like to create a new playlist with these tracks? (yes/no): ").lower()
    if create_new_playlist == 'yes':
        new_playlist_name = input("Enter the name for the new playlist: ")
        new_playlist_id = create_playlist(new_playlist_name)
        add_tracks_to_playlist(new_playlist_id, randomized_tracks)
        print(f"New playlist '{new_playlist_name}' created successfully!")

if __name__ == "__main__":
    main()
