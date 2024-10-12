# import os
# import random
# import spotipy
# from spotipy.oauth2 import SpotifyOAuth
# from dotenv import load_dotenv
# from colorama import init, Fore, Style
# init(autoreset=True)

# # Load environment variables from .env
# load_dotenv()

# # Spotify API credentials
# SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
# SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
# SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# # Spotify OAuth setup
# scope = "playlist-read-private playlist-modify-private playlist-modify-public"
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
#     client_id=SPOTIPY_CLIENT_ID,
#     client_secret=SPOTIPY_CLIENT_SECRET,
#     redirect_uri=SPOTIPY_REDIRECT_URI,
#     scope=scope
# ))

# def get_user_playlists():
#     """Fetch all user playlists."""
#     results = sp.current_user_playlists()
#     playlists = results['items']
#     return playlists

# def display_playlists(playlists):
#     """Display playlists and their IDs."""
#     for idx, playlist in enumerate(playlists):
#         print(f"{idx + 1}: {playlist['name']} (ID: {playlist['id']})")

# def get_playlist_tracks(playlist_id):
#     """Fetch tracks from the playlist."""
#     results = sp.playlist_tracks(playlist_id)
#     tracks = results['items']
#     return tracks

# def shuffle_tracks(tracks):
#     """Shuffle the tracks."""
#     random.shuffle(tracks)
#     return tracks

# def create_new_playlist(name, description):
#     """Create a new playlist for the user."""
#     user_id = sp.current_user()['id']
#     new_playlist = sp.user_playlist_create(user_id, name, description=description)
#     return new_playlist['id']

# def add_tracks_to_playlist(playlist_id, tracks):
#     """Add shuffled tracks to the new playlist."""
#     track_ids = [track['track']['id'] for track in tracks]
#     sp.playlist_add_items(playlist_id, track_ids)

# def main():
#     print("Fetching your playlists...")
#     playlists = get_user_playlists()
    
#     if not playlists:
#         print("No playlists found.")
#         return
    
#     display_playlists(playlists)
    
#     playlist_index = int(input("Enter the number of the playlist you want to shuffle: ")) - 1
#     selected_playlist = playlists[playlist_index]
#     playlist_id = selected_playlist['id']
#     print(f"Selected playlist: {selected_playlist['name']}")
    
#     # Fetch tracks from the selected playlist
#     tracks = get_playlist_tracks(playlist_id)
    
#     if not tracks:
#         print("No tracks found in this playlist.")
#         return
    
#     # Shuffle tracks
#     shuffled_tracks = shuffle_tracks(tracks)
#     print(f"Shuffling {len(tracks)} tracks...")
    
#     # Create a new randomized playlist
#     new_playlist_name = f"Shuffled - {selected_playlist['name']}"
#     new_playlist_description = f"A shuffled version of {selected_playlist['name']}"
#     new_playlist_id = create_new_playlist(new_playlist_name, new_playlist_description)
    
#     # Add shuffled tracks to the new playlist
#     add_tracks_to_playlist(new_playlist_id, shuffled_tracks)
#     print(f"New playlist created: {new_playlist_name}")

# if __name__ == '__main__':
#     main()



import os
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama for colored output in CLI
init(autoreset=True)

# Load environment variables from .env file
load_dotenv()

# Spotify API credentials from environment variables
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

# Spotify scope for accessing playlists
SCOPE = "playlist-modify-public playlist-read-private"

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope=SCOPE))

def get_user_playlists():
    """
    Fetch the current user's playlists and display them in a list for selection.
    """
    playlists = sp.current_user_playlists()
    playlist_list = []

    print(Fore.CYAN + "Your Playlists:")
    print(Style.DIM + "--------------------")
    
    # Display playlists with numbering
    for i, playlist in enumerate(playlists['items']):
        playlist_list.append({'id': playlist['id'], 'name': playlist['name']})
        print(f"{Fore.YELLOW}{i + 1}. {Fore.GREEN}{playlist['name']}")
    
    return playlist_list

def get_playlist_tracks(playlist_id):
    """
    Retrieve tracks from a given Spotify playlist by playlist_id and include their URIs.
    """
    results = sp.playlist_tracks(playlist_id)
    tracks = []
    for item in results['items']:
        track = item['track']
        tracks.append({
            'name': track['name'], 
            'artist': track['artists'][0]['name'], 
            'uri': track['uri']  # Fetch and store the track URI
        })
    return tracks

def randomize_playlist(tracks):
    """
    Randomize the order of tracks in the playlist.
    """
    randomized_tracks = tracks.copy()
    random.shuffle(randomized_tracks)
    return randomized_tracks

def display_tracks(tracks):
    """
    Display the tracks with colored output using colorama.
    """
    print(Fore.CYAN + "Randomized Playlist:")
    print(Style.DIM + "--------------------")
    for i, track in enumerate(tracks):
        print(f"{Fore.YELLOW}{i + 1}. {Fore.GREEN}{track['name']} by {track['artist']}")

def create_new_playlist(user_id, playlist_name):
    """
    Create a new Spotify playlist for the user.
    """
    new_playlist = sp.user_playlist_create(user=user_id, name=playlist_name)
    return new_playlist['id']

def add_tracks_to_playlist(playlist_id, tracks):
    """
    Add tracks to a given Spotify playlist.
    """
    track_uris = [track['uri'] for track in tracks]
    sp.playlist_add_items(playlist_id, track_uris)

def main():
    """
    Main function to handle user input and logic flow.
    """
    # Get current user ID
    user_id = sp.current_user()['id']
    
    # Fetch and display user's playlists
    playlist_list = get_user_playlists()

    # Ask user to select a playlist by number
    playlist_choice = int(input(Fore.BLUE + "Enter the number of the playlist you want to randomize: ")) - 1
    if playlist_choice < 0 or playlist_choice >= len(playlist_list):
        print(Fore.RED + "Invalid choice. Exiting.")
        return
    
    selected_playlist_id = playlist_list[playlist_choice]['id']
    
    # Retrieve the tracks from the selected playlist
    tracks = get_playlist_tracks(selected_playlist_id)

    # Randomize the tracks
    randomized_tracks = randomize_playlist(tracks)

    # Display the randomized playlist with color
    display_tracks(randomized_tracks)

    # Ask user if they want to create a new playlist with the randomized tracks
    create_new = input(Fore.MAGENTA + "Would you like to create a new playlist with these tracks? (yes/no): ").lower()
    if create_new == 'yes':
        playlist_name = input(Fore.CYAN + "Enter the name for the new playlist: ")
        new_playlist_id = create_new_playlist(user_id, playlist_name)
        
        # Add the randomized tracks to the new playlist
        add_tracks_to_playlist(new_playlist_id, randomized_tracks)
        print(Fore.GREEN + f"New playlist '{playlist_name}' created and tracks added successfully!")
    else:
        print(Fore.RED + "No new playlist created. Exiting.")

if __name__ == "__main__":
    main()
