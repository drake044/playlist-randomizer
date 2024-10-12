# Music Playlist Randomizer

![Hacktoberfest](https://img.shields.io/badge/Hacktoberfest-2024-blueviolet)
![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen)

Welcome to the Music Playlist Randomizer project! This tool helps you create random playlists from your music library.

## Features

- Randomly generate playlists from your music library.
- Supports multiple music platforms.
- Easy to configure and use.

## Getting Started

### Prerequisites

- Python 3.x
- Spotify Developer Account

### Installation

1. **Fork the Repository**

   Click on the "Fork" button at the top right of this repository to create your own copy.

2. **Clone Your Fork**

   ```bash
   git clone https://github.com/your-username/music-playlist-randomizer.git
   cd music-playlist-randomizer
   ```

3. **Create a Spotify Developer Account**

   - Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications).
   - Create a new application.
   - Set the callback URL to: `http://localhost:8080/callback/`.

4. **Configure Environment Variables**

   Create a `.env` file in the root directory and add your Spotify credentials:

   ```plaintext
   SPOTIPY_CLIENT_ID='your-client-id'
   SPOTIPY_CLIENT_SECRET='your-client-secret'
   SPOTIPY_REDIRECT_URI='http://localhost:8080/callback/'
   ```

5. **Set Up Virtual Environment and Install Dependencies**

   Create a virtual environment and install the necessary modules from `requirements.txt`:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

### Running the Script

After configuring the environment variables, run the main script:

```bash
python3 main.py
```

## Contributing

We welcome all types of contributions—whether you're fixing a bug, improving documentation, or adding new features. Please read our [contributing guidelines](contributing.md) for more details.

## License

Thank you for checking this out! Happy Hacktoberfest!
