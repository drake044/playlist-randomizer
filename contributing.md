
# Contributing to Music Playlist Randomizer

Thank you for considering contributing to this project! We welcome all types of contributions—whether you're fixing a bug, improving documentation, or adding new features.

## Getting Started

### Step 1: Fork the Repository

1. Click on the "Fork" button at the top right of this repository to create your own copy.
2. Clone your fork to your local machine:
    
    ```bash
    git clone https://github.com/drake044/music-playlist-randomizer.git
    cd music-playlist-randomizer
    
    ```
    
3. make your spotify dev account , create an application.
4. in call back url  put this 
• **http://localhost:8080/callback/**
5. adjust the env according to the client id and secret
here’s an example :

```markdown
SPOTIPY_CLIENT_ID='your-client-id'
SPOTIPY_CLIENT_SECRET='your-client-secret'
SPOTIPY_REDIRECT_URI='[http://localhost:8080/callback/](http://localhost:8080/callback/)'
```

after configuiring the env file , just run the script main.py

 

```markdown
python3 main.py
```

Thankyou!! for checking this out 
Happy Hacktoberfest!