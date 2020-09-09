import colours
import spotify_details

from yeelight import Bulb
import os

import time


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


def set_colour(newr, newg, newb):
    for light_bulb in bulbs:
        if light_bulb is not None:
            light_bulb.set_rgb(newr, newg, newb)
    print(f'Changed colour of all active bulbs to: {newr} {newg} {newb}')


def spotify_colour(last_name):
    url, current_song, image = spotify_details.get_song(resource_path)
    if url != last_name:
        print('Now Playing: ' + current_song['item']['name'] + ' by ' +
              current_song['item']['album']['artists'][0]['name'] + ' on Playlist ' +
              current_song['item']['album']['name'])
        rgb = colours.dominant_colour(image)
        if int(rgb[0]) > 50 or int(rgb[1]) > 50 or int(rgb[2]) > 50:
            set_colour(int(rgb[0]), int(rgb[1]), int(rgb[2]))
    # set_colour() #find the most dominant colour and set it here
    return url, current_song, image, time.time()


def colour_loop(lst, lpt, ln):
    time.sleep(0.5)
    if time.time() - lpt > 1:
        lpt = time.time()
    if time.time() - lst > 3:
        new_name, current_song, new_image, new_time = spotify_colour(ln)
        return new_time, lpt, new_name, new_image
    return lst, lpt, ln, 0


if __name__ == '__main__':
    bulbs = initialise_bulbs()
    for bulb in bulbs:
        if bulb is not None:
            bulb.turn_on()
            bulb.set_brightness(brightness)
    rgb = [180, 180, 0]
    last_name = ''
    last_spotify_time = time.time()
    last_process_time = time.time()
    image = None
    while 1:
        last_spotify_time, last_process_time, last_name, image = colour_loop(last_spotify_time, last_process_time, last_name)
