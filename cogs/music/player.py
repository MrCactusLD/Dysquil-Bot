import time
from discord import FFmpegPCMAudio,Interaction, Embed,Color
from .utils.utils import  get_stream_url,get_stream_search
import logging


#Duration of how long a bot can stay in channel after no songs are playing or no people in channel
INACTIVE_DURATION = 5*60 # Seconds

class Player:
    """
        Class that represents a music player a particular guild.\n
        Args:
        - `guild:int` - guild of a server.
        - `channel_id:int` - id of a starting channel. 
    """

    id = 0   
    def __init__(self,guild:int,channel_id:int, voice,bot):
        self.id = Player.id
        Player.id = Player.id +1
        self.bot = bot
        self.voice = voice
        self.guild = guild
        self.channel_id = channel_id
        self.user = None
        self.is_playing = False
        self.is_paused = False
        self.vc = None
        self.music_queue = []
        self.inactive = 0.0
        self.dead = True
        self.destroy = False
        self.send_embed = False
        self.repeat = False
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        logging.info("Player has been initialised, guild = {0}, id = {1} ".format(self.guild,self.id))

    def player(self):
        """
        Player method that is playing music in an `~.self.vc` that was instanced by `Player.start()` method.\n
        Returns `True` when `INACTIVE_DURATION` has been surpassed.
        """
        if self.vc != None and len(self.music_queue) == 0:
            logging.info("Player instance is waiting for a song, guild = {0}, id = {1} ".format(self.guild,self.id))
            while 1:
                time.sleep(1)
                self.inactive = self.inactive + 1
                if self.inactive >= INACTIVE_DURATION:
                    logging.info("Player wait has exceded wait duration, guild = {0}, id = {1} ".format(self.guild,self.id)) 
                    self.dead = True     
                    self.destroy = True
                    logging.info("Player instance is ready to die")
                    time.sleep(1)                
                    return True
                if len(self.music_queue) != 0:
                    logging.info("Player instance recieved a song to play, guild = {0}, id = {1} ".format(self.guild,self.id))
                    break
        
        if len(self.music_queue) != 0:
            
            try:
                #Put an entire loop in try statement so if someting brakes, the bot can be released easily without causing trouble and getting stuck in a non playable state :/
                #It will do for now :/
                self.inactive = 0
                self.dead = False
                if self.music_queue[0][0][0]["type"] == "sp": 
                    track = self.music_queue[0][0][0]
                    self.music_queue[0][0][0] = get_stream_search(f'{track["artist"]} - {track["name"]}')
                    url = self.music_queue[0][0][0]["url"]
                elif self.music_queue[0][0][0]["url"] == "Custom":
                    track = self.music_queue[0][0][0]
                    self.music_queue[0][0][0]["url"] = get_stream_url(track["id"])
                    url = self.music_queue[0][0][0]["url"]
                elif self.music_queue[0][0][0]["id"] == "Custom":
                    url = self.music_queue[0][0][0]["url"]
                else:
                    url = get_stream_url(id = (self.music_queue[0][0][0]["id"]))
                if url is None:
                    self.music_queue.pop(0)
                    self.player()
                    channel = self.bot.get_channel(self.channel_id)
                    channel.send("Song couldn't be played, Skipping")
                    logging.error("Player instance couldn't retrieve a url to play, guild = {0}, id = {1} ".format(self.guild,self.id))
                else: 
                    if self.music_queue[0][0][0]["name"] != "Custom":
                        self.embed = Embed(title = "Now playing ->",color= Color.purple()).set_footer(icon_url= self.music_queue[0][1], text = "Requested by: "+self.music_queue[0][2])
                        self.embed.add_field(name= "Song name:", value=self.music_queue[0][0][0]["name"])
                        self.embed.add_field(name= "Song Length:", value=self.music_queue[0][0][0]["length"])
                        self.embed.add_field(name= "Song link:", value= "https://www.youtube.com/watch?v=" + self.music_queue[0][0][0]["id"])
                        self.embed.set_image(url=self.music_queue[0][0][0]["thumbnail"])
                        logging.info("Player instance is playing a song, guild = {0}, id = {1}, song_name = {2}".format(self.guild,self.id,self.music_queue[0][0][0]["name"]))
                    self.music_queue.pop(0)
                    if len(self.music_queue) >= 1:
                        self.embed.add_field(name="Remaining songs in queue:", value= len(self.music_queue))
                    self.send_embed = True
                    try:
                        self.vc.play(FFmpegPCMAudio(source=url,**(self.FFMPEG_OPTIONS)), after= lambda e:self.player())   
                    except Exception as e:
                        logging.error(f"Error during playback: {e}")
            except Exception as e:
                logging.info(e)
                logging.info("An Error has occured!")
                logging.info("Resetting the bot to original state :/")
                self.dead = True     
                self.destroy = True
                return True

    async def controller(self):
        if self.dead == True:
            self.player()
        else:
            pass