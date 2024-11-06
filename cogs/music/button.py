import discord

class PaginationView(discord.ui.View):
    current_page : int = 1
    