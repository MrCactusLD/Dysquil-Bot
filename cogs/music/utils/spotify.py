import time
from datetime import datetime

import spotipy
from spotipy.oauth2 import SpotifyOAuth

global scope,file
scope = "user-library-read"
file = 'spotifyClient.txt'


class Spotify():
    def __init__(self):
        self = self

    def setup(self,client_id,client_secret,uri):
        try:
            with open(file,'x') as fp:
                pass
            with open(file,'w') as fp:
                fp.write(f'{client_id}\n{client_secret}\n{uri}')

        except FileExistsError:
            with open(file,'r') as fp:
                fp.readline()

        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,open_browser=False, client_id=client_id, client_secret=client_secret,redirect_uri=uri))

    def get_id(self):
        with open(file,'r') as fp:
            Lines = fp.readlines()
            print(f'{Lines[0][:-2]}\n{Lines[1][:-2]}\n{Lines[2]}')


            self.client_id = Lines[0][:-1]
            self.client_secret = Lines[1][:-1]
            self.uri = Lines[2]

    def get_spotify_playlist(self,url):
        results = []
        offset = 0
        self.get_id()
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,open_browser=False, client_id=self.client_id, client_secret=self.client_secret,redirect_uri=self.uri))
        while True:
            temp = self.sp.playlist_tracks(url,offset=offset)
            for i in temp['items']:
                track = i['track']
                results.append({
                    "name":track['name'],
                    "artist":track['artists'][0]['name'],
                    "type":"sp",
                })

            if temp['total'] == len(results):
                break
            
            else:
                offset = offset+100
                continue
        return results

    def get_spotify_song(self,url):
        self.get_id()
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope,open_browser=False, client_id=self.client_id, client_secret=self.client_secret,redirect_uri=self.uri))
        track = self.sp.track(url)
        song = [{   "name":track['name'],
                    "artist":track['artists'][0]['name'],
                    "type":"sp"
                }]
        return song
