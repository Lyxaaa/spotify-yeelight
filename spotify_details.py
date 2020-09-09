import spotipy
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image
import requests
import json

scope = 'user-read-currently-playing'


def get_song(cache_path):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        scope=scope, cache_path=cache_path + '.cache-light-presence'))
    current_song = sp.currently_playing()
    image_url = current_song['item']['album']['images'][2]['url']
    url, image = download_image(image_url)
    print(current_song)
    return url, current_song, image


def download_image(url):
    response = requests.get(url, stream=True)
    response.raw.decode_content = True
    image = Image.open(response.raw)
    response.close()
    return url, image