import colours
import spotify_details

from yeelight import Bulb
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time
import urllib3
from PIL import Image
import requests
import tkinter
import concurrent.futures

# Before running, you must set the following environment variables
# SPOTIPY_CLIENT_ID = client_id
# SPOTIPY_CLIENT_SECRET = client_secret
# SPOTIPY_REDIRECT_URI = https://google.com/

resource_path = './light_presence_resources/'

makedir = True
for dirname in os.listdir('./'):
    if dirname.__eq__('light_presence_resources'):
        makedir = False
if makedir:
    os.mkdir(resource_path)

README = True
for filename in os.listdir(resource_path):
    if filename.__eq__('README.txt'):
        README = False
if README:
    with open(resource_path + 'README.txt', 'w') as new_file:
        new_file.write("Insert your Yeelight Bulb IP addresses in properties.txt, "
                       "each separated by a single comma and without any spaces.\n"
                       "Invalid IP's will be ignored.\n"
                       "Additionally, before running, you must set the following "
                       "environment variables:\n"
                       "SPOTIPY_CLIENT_ID = client_id\n"
                       "SPOTIPY_CLIENT_SECRET = client_secret\n"
                       "SPOTIPY_REDIRECT_URI = https://google.com/\n\n"
                       "If you do not have these, head to "
                       "https://developer.spotify.com/dashboard/login"
                       " to generate your client id and client secret.")

prop_file = True
for filename in os.listdir(resource_path):
    if filename.__eq__('properties.txt'):
        prop_file = False
if prop_file:
    with open(resource_path + 'properties.txt', 'w') as properties:
        properties.write("ips=192.168.0.2\nbrightness=100")
bulb_ips = []

with open(resource_path + 'properties.txt', 'r') as properties:
    lines = properties.read().split('\n')
    for line in lines:
        contents = line.split('=')
        if contents[0] == 'ips':
            bulb_ips = contents[1].split(',')
        if contents[0] == 'brightness':
            brightness = int(contents[1])
            if brightness <= 0 or brightness > 100:
                brightness = 100


def initialise_bulbs():
    return create_bulb_list(get_bulb_num())


def get_bulb_num():
    bulb_num = 0
    print('Locating bulbs, please wait...')
    for i in range(len(bulb_ips)):
        print(str(int(100 / len(bulb_ips)) * (i + 1)) + '%')
        try:
            check = Bulb(bulb_ips[i]).get_properties()
            bulb_num += 1
        except:
            bulb_num = bulb_num

    if bulb_num == 0:
        print("Please change the contents of " + resource_path +
              'bulb-ips.txt to contain the required information')
        time.sleep(10)
        exit(0)
    return bulb_num


def create_bulb_list(total_bulbs):
    bulb_list = [total_bulbs]
    bulb_num = 0
    for i in range(len(bulb_ips)):
        try:
            check = Bulb(bulb_ips[i]).get_properties()
            bulb_list[bulb_num] = Bulb(bulb_ips[i])
            print('New bulb found at ip ' + bulb_ips[i])
            bulb_num += 1
        except:
            print('No bulb found at ip ' + bulb_ips[i])
    print('Yeelight bulbs found: ' + str(len(bulb_list)))
    return bulb_list


bulbs = initialise_bulbs()

# bulb = Bulb("192.168.0.2")
scope = 'user-read-currently-playing'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope=scope, cache_path=resource_path + '.cache-light-presence'))


def write_property(type, value):
    with open(resource_path + 'properties.txt', 'r') as properties:
        lines = properties.read().split('\n')
        for line in lines:
            contents = line.split('=')
            if contents[0] == 'ips':
                bulb_ips = contents[1].split(',')
            if contents[0] == 'brightness':
                brightness = int(contents[1])
                if brightness <= 0 or brightness > 100:
                    brightness = 100


def get_song(filename):
    current_song = sp.currently_playing()
    image = current_song['item']['album']['images'][2]['url']
    url = image.split('/')
    # print(url)
    source = resource_path + url[4] + '.jpg'
    newfilename, newimage = download_image(image, source, filename)
    return newfilename, current_song, newimage


def download_image(url, source, filename):
    response = requests.get(url, stream=True)
    response.raw.decode_content = True
    newimage = Image.open(response.raw)
    response.close()
    return url, newimage


def set_colour(newr, newg, newb):
    for light_bulb in bulbs:
        if light_bulb is not None:
            light_bulb.set_rgb(newr, newg, newb)
    print(f'Changed colour of all active bulbs to: {newr} {newg} {newb}')


def spotify_colour(last_time, last_name):
    # if time.time() - last_time > 5:
    newname, current_song, image = get_song(last_name)
    if newname != last_name:
        print('Now Playing: ' + current_song['item']['name'] + ' by ' +
              current_song['item']['album']['artists'][0]['name'] + ' on Playlist ' +
              current_song['item']['album']['name'])
        lastname = newname
        rgb = colours.dominant_colour(image)
        # print('1:%d|2:%d|3:%d' % (rgb[0], rgb[1], rgb[2]))
        if int(rgb[0]) > 50 or int(rgb[1]) > 50 or int(rgb[2]) > 50:
            set_colour(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    # set_colour() #find the most dominant colour and set it here
    return str(True), newname, current_song, image, time.time()
    # return str(False)


def draw_ui():
    top = tkinter.Tk()
    top.mainloop()
    return top


if __name__ == '__main__':
    for imgName in os.listdir(resource_path):
        if imgName.endswith('.jpg'):
            os.remove(resource_path + imgName)
    for bulb in bulbs:
        if bulb is not None:
            bulb.turn_on()
            bulb.set_brightness(brightness)
    rgb = [180, 180, 0]
    lastname = ''
    last_spotify_time = time.time()
    last_process_time = time.time()
    image = None
    with concurrent.futures.ThreadPoolExecutor() as exe:
        # base_ui_ticket = exe.submit(tkinter.Tk())
        # base_ui = base_ui_ticket.result()
        while 1:
            time.sleep(0.5)
            if time.time() - last_spotify_time > 3:
                spotify_update = exe.submit(spotify_colour, last_spotify_time, lastname)
                use_update, newname, current_song, new_image, new_time = spotify_update.result()
                if use_update == 'True':
                    lastname = newname
                    last_spotify_time = new_time
                    image = new_image
            if time.time() - last_process_time > 1:
                last_process_time = time.time()
                # print(time.time())
            # ui_update = exe.submit(draw_ui())

#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         ui = executor.submit(draw_ui())
#         while 1:
#             getname = executor.submit(colour_sequence(lastname))
#             print(getname.result())