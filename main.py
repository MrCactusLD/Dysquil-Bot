import os
import discord
from discord.ext import commands
from colorama import Back,Fore,Style
import time
import platform
import logging
import configparser as cf
import db
from cogs.music.utils.spotify import Spotify
from setup import main as stp
from menus import menu
from settings import cls

flag = False

if os.path.isfile("settings.ini") is not True:
    flag = True 

if os.path.isfile("settings.ini") is not True:
    flag = True

os.system(cls)

if flag is True:
    stp()

os.system(cls)

SpotifyParser = cf.ConfigParser()
SpotifyParser.read("spotify.ini")

client_id = SpotifyParser.get('Spotify', 'client_id')
client_secret = SpotifyParser.get('Spotify', 'client_secret')
uri = SpotifyParser.get('Spotify', 'uri')

#Checks if local has auth key
Spotify().setup(client_id=client_id,client_secret=client_secret,uri=uri)

ConfigParser = cf.ConfigParser()
ConfigParser.read("settings.ini")

# All the intents this bot currently has to have,
intents = discord.Intents.all()
intents.message_content = True
intents.voice_states = True
intents.members = True

# For older discord commands, currently not in use but has to be given an variable.
cmd_pre = ","

# Only for testing and debugging purposes
if ConfigParser.get('botSettings','Testing') == "True":
    section = 'TestParameters'
else:
    section = 'WorkingParameters'

guild = ConfigParser.get(section,'guild')

loggings = int(ConfigParser.get('botSettings','logging'))

# Working dir of all the collection of cogs.
cog_dir = ConfigParser.get('botSettings','cogDirectory')                           

# Setup and format of logging system.
if loggings == 1:
    path = ConfigParser.get('botSettings','logDir')
    if not os.path.exists(path[:-1]):
        os.makedirs(path[:-1])

    logging.basicConfig(filename= path + ConfigParser.get('botSettings','mainLog'), level=logging.DEBUG, 
        format='[%(levelname)s][%(asctime)s] - %(filename)s/%(funcName)s[%(lineno)d] = \"%(message)s\"'
        )
    handler = logging.FileHandler(filename= path + ConfigParser.get('botSettings','discordLog'), encoding='utf-8', mode='w')
    
# Prefix for the console.
prfx = (Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S CEST", time.localtime())+ Back.RESET + Fore.WHITE + Style.BRIGHT)


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=cmd_pre, intents=intents,application_id=app_id)
        self.synced = False

    async def setup_hook(self):
        
        reset = (Back.RESET + Fore.WHITE + Style.BRIGHT)
        for dir in os.listdir(cog_dir):
            if os.path.isdir(cog_dir+'/'+dir) and not dir.startswith("__"):
                if os.path.isfile(cog_dir +'/'+ dir + '/'+ dir + '.py'):
                    print(Fore.WHITE + "Loading cog : " + Fore.RED + cog_dir +'/'+ dir + '/'+ dir+'.py' + reset)
                    await self.load_extension('cogs.'+ dir + '.'+ dir)
                else:
                    print(Fore.WHITE + "File not found : " + Fore.RED + cog_dir +'/'+ dir + '/'+ dir+'.py' + reset)
     

    async def on_ready(self):
        reset = (Back.RESET + Fore.WHITE + Style.BRIGHT)
        print(prfx + " Logged in as "+ Fore.YELLOW + self.user.name + reset)
        print(prfx + " Bot ID " + Fore.YELLOW + str(self.user.id) + reset)
        print(prfx + " Discord Version " + Fore.YELLOW + str(discord.__version__) + reset)
        print(prfx + " Python Version " + Fore.YELLOW + str(platform.python_version()) + reset)
        try:
            #synced = await self.tree.sync(guild=discord.Object(id=guild))
            #print(prfx + " Slash commands synced on local guild " + Fore.YELLOW + str(len(synced)) + reset)
            synced = await self.tree.sync()
            print(prfx + " Slash commands synced globally " + Fore.YELLOW + str(len(synced)) + reset)
            print(Fore.YELLOW + "----------------------------------------------")
            print(Fore.GREEN + "Bot is now Ready to use " + Fore.WHITE)
        except Exception as e:
            print(e) 

if __name__ == '__main__':
    try: 
        os.mkdir(os.path.join(os.getcwd(), db.path))
    except:
        pass
    #print()
    conn = db.create_connection(os.path.join(os.getcwd(), db.path) + db.db)
    db.setup_table(conn=conn)
    conn.close()

    bot = menu()
    os.system(cls)
    #print(bot)

    token = bot[2]
    app_id = bot[3]
    bot = MyBot()
    
    if loggings == 1:
        bot.run(token,log_handler=handler)
    else:
        bot.run(token)
