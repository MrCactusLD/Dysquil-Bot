import validators
import httpx
import yt_dlp
import datetime
from requests import get
from .spotify import Spotify
from youtubesearchpython import VideosSearch,Playlist,Video
#༼ つ ◕_◕ ༽つ
#Cool emoji right? 
YTDLP_OPTIONS = {
                'format': 'bestaudio/best',
                'extractaudio': True,
                'audioformat': 'mp3',
                'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
                'restrictfilenames': True,
                'noplaylist': True,
                'nocheckcertificate': True,
                'ignoreerrors': False,
                'logtostderr': False,
                'quiet': True,
                'no_warnings': True,
                'default_search': 'ytsearch',
                'source_address': '0.0.0.0',
            }


def is_audio(url:str):
    """
    \nA function that checks whether a giver url is in audio format.\n
    Args:
    - `url:str`
    """
    if validators.url(url):
        response = httpx.head(url).headers['Content-Type']
        if 'audio' in response:
            return True
    else: 
        return False

def identify(url:str):
    """
    \nA Function that indetifies the source of the url
    Args:
    `url:str`
    """
    ## This is meant for signature check, but currently is checking only url -_-
    if "youtube" in url.lower() or "youtu.be" in url.lower():
        return "Youtube"
    elif "spotify" in url.lower():
        return "Spotify"
    elif "soundcloud" in url.lower():
        return "SoundCloud"
    else: return False

def Youtube_Scrape(url:str):
    """
    \nGets information about the video/song if the song was identified as Youtube
    Args:
    - `url:str`

    \nReturns `list` with one item inside containing a `dict` of items
    """
    Songs =[]
    if "list" in url and not "music" in url:
        Search_Obj = Playlist(url).videos
        for Video_meta in Search_Obj:
            Songs.append({
                            "id": Video_meta['id'],
                            "name" : Video_meta['title'],
                            "thumbnail":Video_meta['thumbnails'][-1]['url'] ,
                            "length": Video_meta['duration'],
                            "url":"Custom",
                            "type":"yt"
                        })
        return Songs
    else:
        Video_meta = Video.getInfo(url)
        Songs.append({
                            "id": Video_meta['id'],
                            "name" : Video_meta['title'],
                            "thumbnail":Video_meta['thumbnails'][-1]['url'] ,
                            "length": str(datetime.timedelta(seconds=int(Video_meta['duration']['secondsText']))),
                            "url":"Custom",
                            "type":"yt"
                        })
    return Songs

def get_spotify_link(search:str):
    """
    \nSearches for a song equivalent on youtube
    Args:
    - `search:str`

    \nReturns `list` with one item inside containing a `dict` of items
    """
    search = VideosSearch(search,limit=1) # Searches the url and retrieves a list of songs
    results = search.result()['result']
    if len(results) > 0:
        Video_meta = results[0] # Takes the first one, cause "probably" its the best :/
        track = {
                    "id": Video_meta['id'],
                    "name" : Video_meta['title'],
                    "thumbnail":Video_meta['thumbnails'][-1]['url'],
                    "length": Video_meta['duration'],
                    "url":'spotify',
                    "type":"sp"
        }
        return track

def Spotify_convert(url:str):
    """
    \nDoes main handling of converting spotify track/playlist to youtube
    Args:
    - `url:str`

    \nReturns a `list` of `dict` containing video meta information needed for further handling.
    """
    Songs = []
    if 'track' in url:
        temp = Spotify().get_spotify_song(url=url)
        Songs.append(get_spotify_link(f'{temp[0]["artist"]} - {temp[0]["name"]}'))
    elif 'playlist' in url:
        Songs = Spotify().get_spotify_playlist(url=url)
  
    return Songs


async def search_audio(search:str):
    """
    \nFunction that searches for audio files, or a supported url to obtain a song.
    Args:
    - `search:str`

    \nReturns a `list` of `dict` containing meta information from the attached source.
    \nReturns `False` if the source is not currently supported.
    \nReturns `None` if the search contained `0` matches.
    """

    Songs = []
    
    if validators.url(search):

        type = identify(search)

        if type == "Youtube":
            
            Songs = Youtube_Scrape(search)
            return Songs
        
        if type == "Spotify":

            Songs = Spotify_convert(search)
            return Songs
        
        if type == "SoundCloud":
            return False

        elif is_audio(search):
            Songs.append({
                "id":"Custom",
                "name":"Custom",
                "thumbnail":"Custom",
                "length":"Custom",
                "url":search,
                "type":"custom"
            })
            return Songs
    else:
        search = VideosSearch(search,limit=1) # Searches the url and retrieves a list of songs
        results = search.result()['result']
        if len(results) > 0:
            Video_meta = results[0] # Takes the first one, cause "probably" its the best :/
            Songs.append({
                        "id": Video_meta['id'],
                        "name" : Video_meta['title'],
                        "thumbnail":Video_meta['thumbnails'][-1]['url'] ,
                        "length": Video_meta['duration'],
                        "url":get_stream_url(Video_meta['id']),
                        "type":"search"
            })   
            return Songs
        else: 
            #Returns None if there aren't any songs found 
            return None

def get_stream_search(src:str):
    """
    \nFunction that searches ytdlp for a song using `ytsearch` method.
    Args:
    - `src:str`

    \nReturns a `dict` containing song meta information
    \nReturns `None` if no tracks were found.
    \nOnly used from player.py to get spotify links :/
    """
    global YTDLP_OPTIONS
    track = None
    with yt_dlp.YoutubeDL(YTDLP_OPTIONS) as ydl:
        try:
            get(src) 
        except:
            video = ydl.extract_info(f"ytsearch:{src}", download=False)['entries'][0]
        else:
            video = ydl.extract_info(src, download=False)
        track = { 
            'id' : video["id"],
            'name' : video["title"],
            'thumbnail': video['thumbnail'],
            'length' : str(datetime.timedelta(seconds=video['duration'])),
            'url' : video['url'],
            'type': 'spotify'
        }
        return track

def get_stream_url(id):
    """
    \nFunction that searches ytdlp using `id` for precise handling of videos.
    Args:
    - `id`

    \nReturns `playUrl:str` - Stream url of the song
    """
    global YTDLP_OPTIONS
    with yt_dlp.YoutubeDL(YTDLP_OPTIONS) as ydl:
        info = ydl.extract_info("https://www.youtube.com/watch?v="+ id, download=False)
        playUrl = info['url']
        return playUrl

