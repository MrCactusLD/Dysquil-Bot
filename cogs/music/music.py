import discord
from discord.ext import commands
from discord import app_commands,Color
import asyncio
from .player import Player
from .utils.utils import search_audio
from colorama import Fore
import random
import logging
import time
from pprint import pprint

PAGINATION = 5

# Class that stores recent message sent for button interaction.
class Messages():
    def __init__(self,guild):
        self.guild = guild
        self.message = None
        self.embed = None
        self.view = None
    async def Default(self):
        self.message = None
        self.embed = None
        self.view = None

# Button class for songs in queue
class QueueUi(discord.ui.View):
        INACTIVE= 30
        def __init__(self, ListOfSongs,embed):
            super().__init__()
            self.value = None
            self.songs= ListOfSongs
            self.edit = False
            self.embed = embed
            self.page = 1
            self.songs = ListOfSongs
            self.button_divider.disabled = True

        def DisableAllButtons(self):
            self.button_next.disabled = True
            self.button_previous.disabled = True 
            self.button_divider.disabled = True
            return self 

        @discord.ui.button(label= " ",style=discord.ButtonStyle.primary,emoji="⏪")
        async def button_previous(self,button:discord.ui.button,interaction : discord.Interaction):
            
            page = self.page - 1
            self.page = self.page - 1
            total_pages = (len(self.songs) + PAGINATION - 1) // PAGINATION
            if page > total_pages or page <= 0:
                self.page = self.page + 1 
                await button.response.defer()
                return
            start_index = (page - 1) * PAGINATION
            end_index = page * PAGINATION
            page_data = self.songs[start_index:end_index]
            i = start_index
            embed = discord.Embed(title = "Songs in queue: "+ str(len(self.songs)),color= discord.Color.purple())
            for x in page_data:
                embed.add_field(name= "id:", value= i+1,inline=True)
                embed.add_field(name= "Song name:", value= x[0][0]["name"],inline=True)
                embed.add_field(name= "", value= "",inline=False) 
                i = i+1

            embed.add_field(name="Page Number ->",value=str(page) + "/" + str(total_pages))
            await self.UpdateMessage(embed=embed, view= self)
            await button.response.defer()

        @discord.ui.button(label= "|_|",style=discord.ButtonStyle.primary)
        async def button_divider(self,button:discord.ui.button,interaction : discord.Interaction):        
            self.button_divider.disabled = True
            await button.response.defer()

        @discord.ui.button(label= " ",style=discord.ButtonStyle.primary,emoji="⏩")
        async def button_next(self,button:discord.ui.button,interaction : discord.Interaction):
            
            page = self.page + 1
            self.page = self.page + 1
            total_pages = (len(self.songs) + PAGINATION - 1) // PAGINATION
            if page > total_pages or page <= 0:
                self.page = self.page - 1
                await button.response.defer()
                return
            start_index = (page - 1) * PAGINATION
            end_index = page * PAGINATION
            page_data = self.songs[start_index:end_index]
            i = start_index
            embed = discord.Embed(title = "Songs in queue: "+ str(len(self.songs)),color= discord.Color.purple())
            for x in page_data:
                embed.add_field(name= "id:", value= i+1,inline=True)
                embed.add_field(name= "Song name:", value= x[0][0]["name"],inline=True)
                embed.add_field(name= "", value= "",inline=False) 
                i = i+1

            embed.add_field(name="Page Number ->",value=str(page) + "/" + str(total_pages))
            await self.UpdateMessage(embed=embed, view= self)
            await button.response.defer()

        async def UpdateMessage(self,embed,view):
            await self.message.edit(embed=embed, view=view)

# Class that stores button styles and buttons for music player. 
class PlayerUi(discord.ui.View):
        def __init__(self, ListOfPlayers):
            super().__init__()
            self.value = None
            self.players= ListOfPlayers
            self.edit = False

        async def DisableAllButtons(self):
            self.button_next.disabled = True
            self.button_pause.disabled = True
            self.button_shuffle.disabled = True
            self.button_stop.disabled = True
            return self 

        @discord.ui.button(label= " ",style=discord.ButtonStyle.primary, emoji="⏸")
        async def button_pause(self,button:discord.ui.button,interaction : discord.Interaction):
            if len(self.players) != 0:
                for x in self.players:
                    if x.guild != button.guild.id:
                        continue
                    if x.vc != None:
                        if x.vc.is_playing():
                            self.button_pause.emoji = "▶️"
                            self.edit = True    
                            x.vc.pause()        
                            await button.response.defer()
                        elif x.vc.is_paused():
                            self.button_pause.emoji = "⏸" 
                            self.edit = True  
                            x.vc.resume()
                            await button.response.defer()
                await button.response.defer()
                
        @discord.ui.button(label= " ",style=discord.ButtonStyle.primary,emoji="⏩")
        async def button_next(self,button:discord.ui.button,interaction : discord.Interaction):
            if len(self.players) != 0:
                for x in self.players:
                    if x.guild != button.guild.id:
                        continue
                    if x.vc != None and x.vc.is_playing():
                        x.vc.stop()
                        await button.response.send_message("The Current song has been skipped!")
                        return
                await button.response.defer()
        
        
        @discord.ui.button(label= " ",style=discord.ButtonStyle.primary, emoji="⏹")
        async def button_stop(self,button:discord.ui.button,interaction : discord.Interaction):
            if len(self.players) != 0:
                for x in self.players:
                    if x.guild != button.guild.id:
                        continue
                    if x.vc != None:
                        await x.vc.disconnect()
                        x.destroy = False
                        x.vc = None
                        x.inactive = 0.0
                        x.dead = True     
                        x.music_queue = []
                        x.destroy = True
                        await button.response.send_message("Bot has stopped playing, and left the voice channel")
                    else: 
                        await button.response.defer()
        
        @discord.ui.button(label= " ",style=discord.ButtonStyle.primary, emoji="🔀")
        async def button_shuffle(self,button:discord.ui.button,interaction : discord.Interaction):
            for i,x in enumerate(self.players):
                if x.guild != button.user.guild.id:
                    continue

                if len(self.players[i].music_queue) != 0:
                    random.shuffle(self.players[i].music_queue)
                    await button.response.send_message("The list was shuffled")
                    return
                await button.response.defer()


class MusicCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.players = []
        self.message = None

    def __self__(self,MyBot:commands.Bot):
        self.bot = MyBot

    def check_guild(self,guild):
        """
        Checks if guild exists in `~self.players`\n
        Args:
            `guild` - guild of the server
        """
        for x in self.players:
            if x.guild == guild:
                return True
        return False

    @commands.Cog.listener()
    async def on_voice_state_update(self,member, before, after,interaction= discord.Interaction):
         # Ignore if change from voice channels not from bot
        print("Connected "+Fore.YELLOW+ str(member.display_name)+Fore.WHITE+ " to voice on " +Fore.YELLOW+ str(after.channel) + Fore.WHITE+": [Before was on "+Fore.YELLOW+ str(before.channel) + Fore.WHITE+"]")
        if not member.id == self.bot.user.id:
            return
        guild = member.guild.id # Guild id
        # Trigger by disconnect()
        if after.channel is None:
            for i,x in enumerate(self.players):
                if x.guild != guild:
                    continue
                if x.vc != None:
                    logging.info("Not connected to voice or ~.vc is not initialised")
                    continue
                logging.info("Player was disconnected manually ,guild = {}".format(x.guild))
                if x.vc is not None:
                    await x.vc.disconnect()
                    x.destroy = False
                    x.vc = None
                    x.inactive = 0.0
                    x.dead = True
                    x.music_queue = []
                    x.destroy = True
                    logging.info("Player is ready to die , guild = {}".format(x.guild))
            return
        else:
            
            for i,x in enumerate(self.players):
                # Initialize and find appropriate player with guild.
                if x.guild != guild:
                    continue
                # Initialize and find appropriate message for guild.
                if self.message is None:
                    self.message = []
                    self.message.append(Messages(x.guild))
                
                for j,k in enumerate(self.message):
                    if k.guild != x.guild:
                        continue
                
                logging.info("Player is waiting for ~.destroy or ~.send_embed , guild = {}".format(x.guild))
                while self.players[i]:
                    await asyncio.sleep(0.1)      
                    if k.view is not None: 
                            if k.view.edit == True:   
                                await k.message.edit(embed=k.embed,view=k.view)              
                    if x.send_embed is True:
                        
                        if k.message is not None:
                            await self.DestroyButton(k)
                            await k.Default()

                        channel = self.bot.get_channel(x.channel_id)
                        view = PlayerUi(self.players)
                        k.message =  await channel.send(embed=x.embed,view=view)
                        k.embed = x.embed
                        k.view = view
                        x.send_embed = False
                        x.embed = False
                        
                    if x.destroy is True:
                        await asyncio.sleep(0.1)
                        if x.vc != None:   
                            await x.vc.disconnect() 
                        channel = self.bot.get_channel(x.channel_id)
                        del self.players[i]
                        await self.DestroyButton(k)
                        await k.Default()
                        logging.info("Player was disconnected and destroyed , guild = {}".format(x.guild))
                        break
                    

    async def DestroyButton(self,Message):
        """
        \nDestroy method that auto sets button to `disabled` after `int:delay` amount of time
        \nReturns False if Message has no `button` element
            Parameters: 
                `int:message` - Message ID
                `int:delay` - delay in seconds
        """
        view = await Message.view.DisableAllButtons()
        await Message.message.edit(embed=Message.embed,view=view)
      

    @app_commands.command(name="play", description="Plays the given url, or searches for the song")
    async def _play(self, interaction: discord.Interaction, song:str):
        """
        `/play` command, that searches the song by `song:str` and plays it.
        """
        await interaction.response.send_message(content = "You're command is being processed, please wait :notes: :notes:")

        # Check if user is in voice channel
        if not interaction.user.voice:
            await interaction.edit_original_response(content = "You are not in a voice channel!")
            return

        if len(self.players) <= 0:
            self.players.append(Player(guild=interaction.user.guild.id, channel_id=interaction.channel.id, voice=interaction.user.voice.channel, bot = self.bot))
        elif self.check_guild(guild= interaction.user.guild.id) == False:
            self.players.append(Player(guild=interaction.user.guild.id, channel_id=interaction.channel.id, voice=interaction.user.voice.channel, bot = self.bot))

        Songs = await search_audio(song)
        if Songs is None or len(Songs) < 1:
            await interaction.edit_original_response(content = "No songs were found matching your search query :sob:")
            return
        
        for x in self.players:
            if x.guild != interaction.user.guild.id:
                continue

            if len(Songs) == 1:
                x.music_queue.append([Songs,interaction.user.display_avatar,interaction.user.display_name])
                x.voice = interaction.user.voice.channel
                x.channel_id = interaction.channel.id
                if len(x.music_queue) == 1:
                    embed = discord.Embed(title = "Song added to queue ->",color= Color.purple()).set_footer(icon_url= interaction.user.display_avatar, text = "Added by by: "+interaction.user.display_name)
                    embed.add_field(name= "Song name:", value=Songs[0]["name"])
                    embed.add_field(name= "Song Length:", value=Songs[0]["length"])
                    embed.add_field(name= "Position in queue:", value= "1")
                    await interaction.edit_original_response(content="",embed=embed)
                else:
                    embed = discord.Embed(title = "Song added to queue ->",color= Color.purple()).set_footer(icon_url= interaction.user.display_avatar, text = "Added by by: " +interaction.user.display_name)
                    embed.add_field(name= "Song name:", value=Songs[0]["name"])
                    embed.add_field(name= "Song Length:", value=Songs[0]["length"])
                    embed.add_field(name= "Position in queue :", value = len(x.music_queue))
                    await interaction.edit_original_response(content="",embed=embed)
            else:
                for i in Songs:
                    s = []
                    s.append(i)
                    x.music_queue.append([s,interaction.user.display_avatar,interaction.user.display_name])

                embed = discord.Embed(title = "Songs added to queue -> ",color= Color.purple()).set_footer(icon_url= interaction.user.display_avatar, text = "Added by by: "+interaction.user.display_name)
                embed.add_field(name="Number of songs :", value= len(Songs))
                await interaction.edit_original_response(content="",embed=embed)

            if x.dead is True: 
                if x.vc is None:
                    x.vc = await x.voice.connect(reconnect=True, self_deaf=True)
                    await x.controller()

    @app_commands.command(name="skip", description="Skips the current playing song")
    async def _skip(self,interaction:discord.Interaction) -> None:
        """
        `/skip` command, that skips the current playing song, if there is any.
        """
        if len(self.players) != 0:
            for x in self.players:
                if x.guild != interaction.user.guild.id:
                    continue
                if x.vc != None and x.vc.is_playing():
                    x.vc.stop()
                    await interaction.response.send_message("The Current song has been skipped!")
                    return
        await interaction.response.send_message("The bot is currently not playing any music!")    
    
    @app_commands.command(name="remove",description="Removes the song from the current queue")
    async def _remove(self,interaction:discord.Interaction, id:int) -> None:
        """
        `/remove` command, that removes a song from queue by `id:int`
        """
        rl_id= (id-1)
        if len(self.players) != 0:
            for x in self.players:
                if x.guild != interaction.user.guild.id:
                    continue
                if len(x.music_queue) >= 1 and len(x.music_queue) >= rl_id:
                    await interaction.response.send_message("Removed song: "+str(x.music_queue[rl_id][0][0]["name"]))
                    x.music_queue.pop(rl_id)
                else:
                    await interaction.response.send_message("Sorry, couldn't find the song in queue")


    @app_commands.command(name="stop",description="Stops the music and clears the queue")
    async def _stop(self,interaction:discord.Interaction):
        """
        `/stop` command, that stops the bot, and leaves the voice channel
        """
        if len(self.players) != 0:
            for x in self.players:
                if x.guild != interaction.user.guild.id:
                    continue
                if x.vc != None:
                    await x.vc.disconnect()
                    x.destroy = False
                    x.vc = None
                    x.inactive = 0.0
                    x.dead = True     
                    x.music_queue = []
                    x.destroy = True
                    await interaction.response.send_message("Bot has stopped playing, and left the voice channel")
                else: 
                    await interaction.response.send_message("Bot is not connected to the voice channel")


    @app_commands.command(name="queue",description="Lists the songs in queue along with its ids")
    async def _queue(self,interaction:discord.Interaction):
        """
        `/queue` command, that lists all songs in queue by `page` number.
        """

        if len(self.players) != 0:
            for x in self.players:
                if x.guild != interaction.user.guild.id:
                    continue

                page = 1
                total_pages = (len(x.music_queue) + PAGINATION - 1) // PAGINATION
                if page > total_pages or page <= 0:
                    await interaction.response.send_message("No Songs in queue!")
                    return
                start_index = (page - 1) * PAGINATION
                end_index = page * PAGINATION
                page_data = x.music_queue[start_index:end_index]
                i = start_index
                embed = discord.Embed(title = "Songs in queue: "+ str(len(x.music_queue)),color= discord.Color.purple())
                for j in page_data:
                    embed.add_field(name= "id:", value= i+1,inline=True)
                    embed.add_field(name= "Song name:", value= j[0][0]["name"],inline=True)
                    embed.add_field(name= "", value= "",inline=False) 
                    i = i+1

                embed.add_field(name="Page Number ->",value=str(page) + "/" + str(total_pages))
                view = QueueUi(ListOfSongs=x.music_queue , embed=embed)
                await interaction.response.send_message(embed=embed,view=view)
                message = await interaction.original_response()
                view.message = message

        else:
            await interaction.response.send_message("No songs :/")
    
    @app_commands.command(name="shuffle", description="shuffles the current list of the songs")
    async def _shuffle(self, interaction:discord.Interaction):
        """ 
        `/shuffle` command, that takes the `music_queue` list, and reorganizes it randomly.
        """
        for i,x in enumerate(self.players):
            if x.guild != interaction.user.guild.id:
                continue

            if len(self.players[i].music_queue) != 0:
                random.shuffle(self.players[i].music_queue)
                await interaction.response.send_message("The list was shuffled")
                return
        await interaction.response.send_message("The bot is not in a voice channel or it doesn't have any songs in queue")


async def setup(MyBot:commands.Bot) -> None:
    await MyBot.add_cog(MusicCog(MyBot)) 


