#Version: 1.5
#GitHub: https://github.com/Simoneeeeeeee/Discord-Select-Menu-Ticket-Bot
#Discord: https://discord.gg/simone

import discord
import asyncio
import json
from discord.ui import *
from discord.ext import commands
from discord.ext.commands import has_permissions
from pytz import timezone

with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

BOT_TOKEN = config["token"]  #Bot Token create bot on discord.dev
BOT_PREFIX = config["prefix"] #Prefix for the Commands if you dont use Slash Commands
TIMEZONE = config["timezone"] #Timezone for the Log you find all timezones at https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568

GUILD_ID = config["guild_id"] #Server ID
TICKET_CHANNEL = config["ticket_channel_id"] #Where the bot should send the Embed + SelectMenu

CATEGORY_ID1 = config["category_id_1"] #Support1 Channel
CATEGORY_ID2 = config["category_id_2"] #Support2 Channel

TEAM_ROLE1 = config["team_role_id_1"] #Permissions for Support1
TEAM_ROLE2 = config["team_role_id_1"] #Permissions for Support2

LOG_CHANNEL = config["log_channel_id"] #Log Channel

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    bot.add_view(MyView())
    bot.add_view(delete())

class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="support",
        placeholder="Choose a Ticket option",
        options=[
            discord.SelectOption(
                label="Support1",  #Name of the 1 Option
                emoji="❓",        # Emoji of the 1 Option
                value="support1"   #Don't change this value!
            ),
            discord.SelectOption(
                label="Support2",  #Name of the 2 Option
                emoji="❓",        # Emoji of the 2 Option
                value="support2"   #Don't change this value!
            )
        ]
    )
    async def callback(self, select, interaction):
        if "support1" in interaction.data['values']:
            if interaction.channel.id == TICKET_CHANNEL:
                guild = bot.get_guild(GUILD_ID)
                for ticket in guild.channels:
                    if str(interaction.user.id) in ticket.name:
                        embed = discord.Embed(title=f"You can only open one Ticket!", description=f"Here is your opend Ticket --> {ticket.mention}", color=0xff0000)
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        await asyncio.sleep(3)
                        embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
                        await interaction.message.edit(embed=embed, view=MyView())
                        return
                category = bot.get_channel(CATEGORY_ID1)
                ticket_channel = await guild.create_text_channel(f"ticket-{interaction.user.id}", category=category,
                                                                topic=f"{interaction.user.id}")

                await ticket_channel.set_permissions(guild.get_role(TEAM_ROLE1), send_messages=True, read_messages=True, add_reactions=False,
                                                    embed_links=True, attach_files=True, read_message_history=True,
                                                    external_emojis=True)
                await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=False,
                                                    embed_links=True, attach_files=True, read_message_history=True,
                                                    external_emojis=True)
                await ticket_channel.set_permissions(guild.default_role, send_messages=False, read_messages=False, view_channel=False)
                embed = discord.Embed(description=f'Welcome {interaction.user.mention}!\n'
                                                   'Type something here',
                                                color=discord.colour.Color.blue())
                await ticket_channel.send(embed=embed, view=delete())

                embed = discord.Embed(description=f'📬 Ticket was Created! Look here --> {ticket_channel.mention}',
                                        color=discord.colour.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                await asyncio.sleep(3)
                embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
                await interaction.message.edit(embed=embed, view=MyView())
                return
        if "support2" in interaction.data['values']:
            if interaction.channel.id == TICKET_CHANNEL:
                guild = bot.get_guild(GUILD_ID)
                for ticket in guild.channels:
                    if str(interaction.user.id) in ticket.name:
                        embed = discord.Embed(title=f"You can only open one Ticket", description=f"Here is your opend Ticket --> {ticket.mention}", color=0xff0000)
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                        await asyncio.sleep(3)
                        embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
                        await interaction.message.edit(embed=embed, view=MyView())
                        return 
                category = bot.get_channel(CATEGORY_ID2)
                ticket_channel = await guild.create_text_channel(f"ticket-{interaction.user.id}", category=category,
                                                                    topic=f"{interaction.user.id}")
                await ticket_channel.set_permissions(guild.get_role(TEAM_ROLE2), send_messages=True, read_messages=True, add_reactions=False,
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=False,
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                await ticket_channel.set_permissions(guild.default_role, send_messages=False, read_messages=False, view_channel=False)
                embed = discord.Embed(description=f'Welcome {interaction.user.mention}!\n'
                                                   'Type something here',
                                                    color=discord.colour.Color.blue())
                await ticket_channel.send(embed=embed, view=delete())

                embed = discord.Embed(description=f'📬 Ticket was Created! Look here --> {ticket_channel.mention}',
                                        color=discord.colour.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True)

                await asyncio.sleep(3)
                embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
                await interaction.message.edit(embed=embed, view=MyView())
        return

class delete(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket 🎫", style = discord.ButtonStyle.red, custom_id="close")
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        channel = bot.get_channel(LOG_CHANNEL)

        fileName = f"{interaction.channel.name}.txt"
        with open(fileName, "w", encoding='utf-8') as file:
            async for msg in interaction.channel.history(limit=None, oldest_first=True):
                time = msg.created_at.replace(tzinfo=timezone('UTC')).astimezone(timezone(TIMEZONE))
                file.write(f"{time} - {msg.author.display_name}: {msg.clean_content}\n")

        embed = discord.Embed(
                description=f'Ticket is closing in 5Sec.',
                color=0xff0000)
        embed2 = discord.Embed(title="Ticket Closed!", description=f"Ticket Name: {interaction.channel.name}\n Ticket from: <@{interaction.channel.topic}>\n Closed from: {interaction.user.name}\n Transcript: ", color=discord.colour.Color.blue())
        file = discord.File(fileName)
        await interaction.response.send_message(embed=embed)
        await channel.send(embed=embed2)
        await asyncio.sleep(1)
        await channel.send(file=file)
        await asyncio.sleep(5)
        await interaction.channel.delete(reason="Ticket closed by user")

@bot.command()
@has_permissions(administrator=True)
async def ticket(ctx):
    channel = bot.get_channel(TICKET_CHANNEL)
    embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
    await channel.send(embed=embed, view=MyView())

@bot.command()
async def close(ctx):
    channel = bot.get_channel(LOG_CHANNEL)

    fileName = f"{ctx.channel.name}.txt"
    with open(fileName, "w", encoding='utf-8') as file:
        async for msg in ctx.channel.history(limit=None, oldest_first=True):
            time = msg.created_at.replace(tzinfo=timezone('UTC')).astimezone(timezone(f"{TIMEZONE}"))
            file.write(f"{time} - {msg.author.display_name}: {msg.clean_content}\n")

    embed = discord.Embed(description=f'Ticket is closing in 5Sec.', color=0xff0000)
    embed2 = discord.Embed(title="Ticket Closed!", description=f"Ticket Name: {ctx.channel.name}\n Ticket from: <@{ctx.channel.topic}>\n Closed from: {ctx.author.name}\n Transcript: ", color=discord.colour.Color.blue())
    file = discord.File(fileName)
    await ctx.reply(embed=embed)
    await channel.send(embed=embed2)
    await asyncio.sleep(1)
    await channel.send(file=file)
    await asyncio.sleep(5)
    await ctx.channel.delete(reason="Ticket closed by user")

@bot.command()
async def add(ctx, member: discord.Member):
    category1 = bot.get_channel(CATEGORY_ID1)
    category2 = bot.get_channel(CATEGORY_ID2)
    if ctx.channel.category_id == CATEGORY_ID1 or ctx.channel.category_id == CATEGORY_ID2:
        await ctx.channel.set_permissions(member, send_messages=True, read_messages=True, add_reactions=False,
                                            embed_links=True, attach_files=True, read_message_history=True,
                                            external_emojis=True)
        embed = discord.Embed(description=f'Added {member.mention} to this Ticket <#{ctx.channel.id}>! \n Use !remove @User or ID to remove a User.', color=discord.colour.Color.green())
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(description=f'You can only use this command in a Ticket', color=discord.colour.Color.red())
        await ctx.reply(embed=embed)

@bot.command()
async def remove(ctx, member: discord.Member):
    category1 = bot.get_channel(CATEGORY_ID1)
    category2 = bot.get_channel(CATEGORY_ID2)
    if ctx.channel.category_id == CATEGORY_ID1 or ctx.channel.category_id == CATEGORY_ID2:
        await ctx.channel.set_permissions(member, send_messages=False, read_messages=False, add_reactions=False,
                                            embed_links=False, attach_files=False, read_message_history=False,
                                            external_emojis=False)
        embed = discord.Embed(description=f'Removed {member.mention} from this Ticket <#{ctx.channel.id}>! \n Use !add @User or ID to add a User.', color=discord.colour.Color.green())
        await ctx.reply(embed=embed)
    else:
        embed = discord.Embed(description=f'You can only use this command in a Ticket', color=discord.colour.Color.red())
        await ctx.reply(embed=embed)

bot.run(BOT_TOKEN)
