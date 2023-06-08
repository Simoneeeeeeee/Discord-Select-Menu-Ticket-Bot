#Version: 1.7
#GitHub: https://github.com/Simoneeeeeeee/Discord-Select-Menu-Ticket-Bot
#Discord: discord.gg/ycZDpat7dB

import discord
import json
from discord import *
from discord.ext import commands, tasks
from cogs.ticket_system import Ticket_System
from cogs.ticket_commands import Ticket_Command

with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

BOT_TOKEN = config["token"]  #Bot Token create bot on discord.dev
GUILD_ID = config["guild_id"] #Server ID
CATEGORY_ID1 = config["category_id_1"] #Category ID 1
CATEGORY_ID2 = config["category_id_2"] #Category ID 2

bot = commands.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'Bot Logged | {bot.user.name}')
    richpresence.start()

#Bot Status, Counting all opened Tickets in the Server. You need to add/change things if you have more or less than 2 Categories
@tasks.loop(minutes=1)
async def richpresence():
    guild = bot.get_guild(GUILD_ID)
    category1 = discord.utils.get(guild.categories, id=int(CATEGORY_ID1))
    category2 = discord.utils.get(guild.categories, id=int(CATEGORY_ID2))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'Tickets | {len(category1.channels) + len(category2.channels)}'))

bot.add_cog(Ticket_System(bot))
bot.add_cog(Ticket_Command(bot))
bot.run(BOT_TOKEN)
