import validators
import httpx
from pytube import YouTube,Search,Playlist
import yt_dlp
from pytube.exceptions import VideoUnavailable, AgeRestrictedError
import logging
import datetime
from requests import get
from .spotify import Spotify

YT_PRFX = "https://www.youtube.com"
YT_IMG_PRFX = "https://www.youtube.com"
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
    A function that checks whether a giver url is in audio format.\n
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
    ## This is meant for signature check, but currently is only checking only url -_-
    if "youtube" in url.lower() or "youtu.be" in url.lower():
        return "Youtube"
    elif "spotify" in url.lower():
        return "Spotify"
    elif "soundcloud" in url.lower():
        return "SoundCloud"
    else: return False

def Youtube_Scrape(url:str):
    Songs =[]
    if "list" in url:
        Object = Playlist(url).videos
        for x in Object:
            Songs.append({
                            "id": x.video_id,
                            "name" : x.title,
                            "thumbnail":x.thumbnail_url ,
                            "length": str(datetime.timedelta(seconds=x.length)),
                            "url":x.watch_url,
                            "type":"yt"
                        })

    else:
        Object = YouTube(url)
        Songs.append({
                            "id": Object.video_id,
                            "name" : Object.title,
                            "thumbnail":Object.thumbnail_url ,
                            "length": str(datetime.timedelta(seconds=Object.length)),
                            "url":Object.watch_url,
                            "type":"yt"
                        })
    return Songs


def Spotify_convert(url):
    Songs = []
    if 'track' in url:
        Songs = Spotify().get_spotify_song(url=url)
        temp = get_spotify_link(f'{Songs[0]["artist"]} - {Songs[0]["name"]}')
        Songs[0]["length"] = temp[0]["length"]
        Songs[0]["thumbnail"] = temp[0]["thumbnail"]
    elif 'playlist' in url:
        Songs = Spotify().get_spotify_playlist(url=url)
        
    return Songs

def search(arg:any):
    global YTDLP_OPTIONS
    with yt_dlp.YoutubeDL(YTDLP_OPTIONS) as ydl:
        try:
            get(arg) 
        except:
            video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else:
            video = ydl.extract_info(arg, download=False)
        return video


async def search_audio(search:str):
    """
    \nFunction that searches for audio file and retrieves a `list` of `dicts` with information about the given parameter.
    \nIf the audio file is hosted privately on a server, it will return a `list` of `dicts` containing "Custom" for every parameter except for `~["url"]`
    \nIf audio file is scrape protected, then it will return `None` 
    \nArgs:
    - `search:str`
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
        search = Search(search) # Searches the url and retrieves a list of songs
        results = search.results
        if len(results) > 0:
            result = results[0] # Finds the best match
            Songs.append({
                        "id": result.video_id,
                        "name" : result.title,
                        "thumbnail":result.thumbnail_url ,
                        "length": str(datetime.timedelta(seconds=result.length)),
                        "url":result.watch_url,
                        "type":"search"
            })   
            return Songs
        else: 
            return False

def get_link_ytdlp(id):
    """
    Separate function that is here only to extract age restricted urls, since pytube requires login :) .i.
    """
    global YTDLP_OPTIONS
    with yt_dlp.YoutubeDL(YTDLP_OPTIONS) as ydl:
        info = ydl.extract_info("https://www.youtube.com/watch?v="+ id, download=False)
        playUrl = info['url']
        return playUrl

def get_spotify_link(search):
    with yt_dlp.YoutubeDL(YTDLP_OPTIONS) as ydl:
        try:
            get(search) 
        except:
            video = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
        else:
            video = ydl.extract_info(search, download=False)
        track = [{
            "id":video["id"],
            "name":video["title"],
            "thumbnail":video["thumbnail"],
            "length": str(datetime.timedelta(seconds=video["duration"])),
            "url":video["url"],
            "type":"sp"

        }]
        return track
     
def get_yt_song(id:str):
    """
    Scrapes YouTube video by `id` and retrieves download url.\n
    Args:
    `id` - Yotube video id
    """
    try:
        yt = YouTube.from_id(id)
        str_data = yt.streaming_data["adaptiveFormats"]
    except AgeRestrictedError:
        logging.warning("Video was age restricted, trying to get url from yt-dlp ...")
        songUrl = get_link_ytdlp(id)
        if songUrl is not None: 
            logging.info("url extraction was succesfull.")
            logging.info("url = {} ".format(songUrl))
            return songUrl
        else:
            logging.error("couldn't get the age restricted video.")
            return None
    except VideoUnavailable:
        logging.error("Video was unavailable")
        return None
    for x in str_data:
        if "audioQuality" in x:
            if x["audioQuality"] == "AUDIO_QUALITY_MEDIUM":
                logging.debug("Song was recovered succesfully")
                return x["url"]
    return None

