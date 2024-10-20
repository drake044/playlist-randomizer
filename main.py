
import csv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
import colorama
from colorama import Fore, Style
from dotenv import load_dotenv
from tqdm import tqdm
import os
import time

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
    genres = artist.get('genres', [])
    return genres

# Fetch recommended tracks based on genres
def fetch_recommended_tracks(genres, limit=10):
    recommendations = []
    unique_genres = list(set(genres))  # Remove duplicate genres
    
    # Fallback genre if no recommendations found for the provided genres
    fallback_genres = ['pop', 'electronic']
    
    # If no valid genres found, default to fallback genres
    if not unique_genres:
        unique_genres = fallback_genres
    
    print(f"Fetching recommendations for genres: {unique_genres}")  # Debug statement
    
    # Try fetching recommendations for each genre until limit is reached
    with tqdm(total=limit, desc="Fetching Recommendations", ncols=100) as pbar:
        for genre in unique_genres:
            if len(recommendations) >= limit:
                break
            try:
                recs = sp.recommendations(seed_genres=[genre], limit=min(5, limit-len(recommendations)))
                if recs and recs['tracks']:
                    recommendations.extend(recs['tracks'])
                    pbar.update(len(recs['tracks']))
            except Exception as e:
                print(f"Error fetching recommendations for genre {genre}: {e}")
    
    # If we still don't have enough recommendations, use fallback genres
    if len(recommendations) < limit:
        print(f"Insufficient recommendations. Fetching fallback genres: {fallback_genres}")
        for genre in fallback_genres:
            if len(recommendations) >= limit:
                break
            try:
                recs = sp.recommendations(seed_genres=[genre], limit=min(5, limit-len(recommendations)))
                recommendations.extend(recs['tracks'])
                pbar.update(len(recs['tracks']))
            except Exception as e:
                print(f"Error fetching fallback recommendations for genre {genre}: {e}")
    
    return recommendations[:limit]

# Export track details to CSV
def export_tracks_to_csv(tracks, filename="randomized_tracks.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the header row
        writer.writerow(['Track Name', 'Artist', 'Duration (Minutes)', 'Genres', 'Track URI'])
        
        # Write each track's information
        for track in tracks:
            track_name = track['track']['name']
            artist_name = track['track']['artists'][0]['name']
            duration_ms = track['track']['duration_ms']
            duration_min = round(duration_ms / 60000, 2)  # Convert to minutes
            track_genres = fetch_genres(track['track']['id'])
            track_uri = track['track']['uri']
            
            # Write the row to the CSV file
            writer.writerow([track_name, artist_name, duration_min, ', '.join(track_genres), track_uri])
        
    print(f"Track information exported to {filename}")

# Randomize tracks with optional genre-based recommendations (discovery mode)
def randomize_with_genres(tracks, discovery_mode=False, total_limit=10):
    genres_set = set()

    print("\nFetching genres from current playlist...")
    for track in tracks:
        genres = fetch_genres(track['track']['id'])
        genres_set.update(genres)

    if discovery_mode:
        recommended_tracks = fetch_recommended_tracks(list(genres_set), limit=(total_limit - len(tracks)))
        all_tracks = tracks + [{'track': rec} for rec in recommended_tracks]
    else:
        all_tracks = tracks

    random.shuffle(all_tracks)
    all_tracks = all_tracks[:total_limit]

    # Debug: Print URIs of all tracks to ensure both original and recommended are included
    for idx, track in enumerate(all_tracks):
        print(f"{idx + 1}: {track['track']['name']} - {track['track']['uri']}")

    return all_tracks

# Add tracks to a playlist with a progress bar
def add_tracks_to_playlist(playlist_id, tracks):
    track_uris = [track['track']['uri'] for track in tracks]
    
    # Add progress bar for adding tracks
    print("\nAdding tracks to the new playlist:")
    with tqdm(total=len(track_uris), desc="Adding Tracks", ncols=100) as pbar:
        for i in range(0, len(track_uris), 100):
            sp.playlist_add_items(playlist_id, track_uris[i:i+100])
            pbar.update(100 if len(track_uris) - i > 100 else len(track_uris) - i)

# Simulate progress bar for playlist creation
def simulate_playlist_creation_progress():
    print("\nCreating new playlist...")
    with tqdm(total=100, desc="Creating Playlist", ncols=100) as pbar:
        for _ in range(5):
            time.sleep(0.3)
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
    
    # Ask the user if they want to randomize with genres
    use_genre_based_randomization = input("\nDo you want to randomize and include tracks from similar genres? (yes/no): ").lower()
    discovery_mode = use_genre_based_randomization == 'yes'
    
    # Randomize and optionally add new tracks
    total_limit = int(input("Enter the total number of tracks you want in the final playlist: "))
    randomized_tracks = randomize_with_genres(tracks, discovery_mode=discovery_mode, total_limit=total_limit)
    
    print("\nRandomized Playlist:")
    print("--------------------")
    for idx, track in enumerate(randomized_tracks, start=1):
        print(f"{idx}. {track['track']['name']} by {track['track']['artists'][0]['name']}")
    
    # Export track details to a CSV file
    export_to_csv = input("\nWould you like to export the track details to a CSV file? (yes/no): ").lower()
    if export_to_csv == 'yes':
        export_tracks_to_csv(randomized_tracks)
    
    create_new_playlist = input("\nWould you like to create a new playlist with these tracks? (yes/no): ").lower()
    if create_new_playlist == 'yes':
        playlist_name = input("Enter a name for the new playlist: ")
        new_playlist_id = create_playlist(playlist_name)
        add_tracks_to_playlist(new_playlist_id, randomized_tracks)
        print(f"New playlist '{playlist_name}' created successfully!")

if __name__ == "__main__":
    main()
