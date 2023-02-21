import discord
import asyncio
from discord.ui import *
from discord.ext import commands
from discord.ext.commands import has_permissions
from pytz import timezone

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

GUILD_ID = 123 #Server ID
TICKET_CHANNEL = 123 #Where the bot should send the Embed + SelectMenu

CATEGORY_ID1 = 123 #Support1 Channel
CATEGORY_ID2 = 123 #Support2 Channel

TEAM_ROLE1 = 123 #Permissions for Support1
TEAM_ROLE2 = 123 #Permissions for Support2

LOG_CHANNEL = 123 #Log Channel

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
                label="Support1",
                emoji="❓",
                value="support1"
            ),
            discord.SelectOption(
                label="Support2",
                emoji="❓",
                value="support2"
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
                                                                topic=f"Ticket from {interaction.user} \nUser-ID: {interaction.user.id}")

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
                                                                    topic=f"Ticket from {interaction.user} \nUser-ID: {interaction.user.id}")
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
        with open(fileName, "w") as file:
            async for msg in interaction.channel.history(limit=None, oldest_first=True):
                time = msg.created_at.replace(tzinfo=timezone('UTC')).astimezone(timezone('Europe/Berlin'))
                file.write(f"{time} - {msg.author.display_name}: {msg.clean_content}\n")

        embed = discord.Embed(
                description=f'Ticket is closing in 5Sec.',
                color=0xff0000)
        embed2 = discord.Embed(title="Ticket Closed!", description=f"Ticket-Name: {interaction.channel.name}\n Closed-From: {interaction.user.name}\n Transcript: ", color=discord.colour.Color.blue())
        file = discord.File(fileName)
        await channel.send(embed=embed2)
        await asyncio.sleep(1)
        await channel.send(file=file)
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)
        await interaction.channel.delete(reason="Ticket closed by user")

@bot.command()
@has_permissions(administrator=True)
async def ticket(ctx):
    channel = bot.get_channel(TICKET_CHANNEL)
    embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
    await channel.send(embed=embed, view=MyView())

bot.run("Token")
