import discord
import asyncio
import json
import sqlite3
import datetime
import chat_exporter
import io
from discord.ext import commands

with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

GUILD_ID = config["guild_id"] #Server ID
TICKET_CHANNEL = config["ticket_channel_id"] #Where the bot should send the Embed + SelectMenu

CATEGORY_ID1 = config["category_id_1"] #Support1 Category ID
CATEGORY_ID2 = config["category_id_2"] #Support2 Category ID

TEAM_ROLE1 = config["team_role_id_1"] #Staff Permissions for Support1
TEAM_ROLE2 = config["team_role_id_2"] #Staff Permissions for Support2

LOG_CHANNEL = config["log_channel_id"] #Log Channel ID
TIMEZONE = config["timezone"] #Timezone for the Timestamp https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List

conn = sqlite3.connect('user.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS ticket 
           (id INTEGER PRIMARY KEY AUTOINCREMENT, discord_name TEXT, discord_id INTEGER, ticket_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()

class Ticket_System(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot Loaded | ticket_system.py ✅')
        self.bot.add_view(MyView(bot=self.bot))
        self.bot.add_view(CloseButton(bot=self.bot))
        self.bot.add_view(TicketOptions(bot=self.bot))

    @commands.Cog.listener()
    async def on_bot_shutdown():
        cur.close()
        conn.close()

class MyView(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.select(
        custom_id="support",
        placeholder="Choose a Ticket option",
        options=[
            discord.SelectOption(
                label="Support1",  #Name of the 1 Option
                emoji="❓",        # Emoji of the 1 Option
                value="support1"   #Don't change this value!!!!
            ),
            discord.SelectOption(
                label="Support2",  #Name of the 2 Option
                emoji="❓",        # Emoji of the 2 Option
                value="support2"   #Don't change this value!!!!
            )
        ]
    )
    async def callback(self, select, interaction):
        if "support1" in interaction.data['values']:
            if interaction.channel.id == TICKET_CHANNEL:
                guild = self.bot.get_guild(GUILD_ID)
                member_id = interaction.user.id
                member_name = interaction.user.name
                cur.execute("SELECT discord_id FROM ticket WHERE discord_id=?", (member_id,))
                existing_ticket = cur.fetchone()
                if existing_ticket is None:
                    cur.execute("INSERT INTO ticket (discord_name, discord_id) VALUES (?, ?)", (member_name, member_id))
                    conn.commit()
                    cur.execute("SELECT id FROM ticket WHERE discord_id=?", (member_id,))
                    ticket_number = cur.fetchone()
                    category = self.bot.get_channel(CATEGORY_ID1)
                    ticket_channel = await guild.create_text_channel(f"ticket-{ticket_number}", category=category,
                                                                    topic=f"{interaction.user.id}")

                    await ticket_channel.set_permissions(guild.get_role(TEAM_ROLE1), send_messages=True, read_messages=True, add_reactions=False,
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=False,
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(guild.default_role, send_messages=False, read_messages=False, view_channel=False)
                    embed = discord.Embed(description=f'Welcome {interaction.user.mention},\n'
                                                       'describe your Problem and our Support will help you soon.',
                                                    color=discord.colour.Color.blue())
                    await ticket_channel.send(embed=embed, view=CloseButton(bot=self.bot))

                    embed = discord.Embed(description=f'📬 Ticket was Created! Look here --> {ticket_channel.mention}',
                                            color=discord.colour.Color.green())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    await asyncio.sleep(1)
                    embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
                    await interaction.message.edit(embed=embed, view=MyView(bot=self.bot))
                else:
                    embed = discord.Embed(title=f"You already have a open Ticket", color=0xff0000)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    await asyncio.sleep(1)
                    embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
                    await interaction.message.edit(embed=embed, view=MyView(bot=self.bot))
        if "support2" in interaction.data['values']:
            if interaction.channel.id == TICKET_CHANNEL:
                guild = self.bot.get_guild(GUILD_ID)
                member_id = interaction.user.id
                member_name = interaction.user.name
                cur.execute("SELECT discord_id FROM ticket WHERE discord_id=?", (member_id,))
                existing_ticket = cur.fetchone()
                if existing_ticket is None:
                    cur.execute("INSERT INTO ticket (discord_name, discord_id) VALUES (?, ?)", (member_name, member_id))
                    conn.commit()
                    cur.execute("SELECT id FROM ticket WHERE discord_id=?", (member_id,))
                    ticket_number = cur.fetchone()
                    category = self.bot.get_channel(CATEGORY_ID2)
                    ticket_channel = await guild.create_text_channel(f"ticket-{ticket_number}", category=category,
                                                                    topic=f"{interaction.user.id}")

                    await ticket_channel.set_permissions(guild.get_role(TEAM_ROLE2), send_messages=True, read_messages=True, add_reactions=False,
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=False,
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(guild.default_role, send_messages=False, read_messages=False, view_channel=False)
                    embed = discord.Embed(description=f'Welcome {interaction.user.mention},\n'
                                                       'how can i help you?',
                                                    color=discord.colour.Color.blue())
                    await ticket_channel.send(embed=embed, view=CloseButton(bot=self.bot))

                    embed = discord.Embed(description=f'📬 Ticket was Created! Look here --> {ticket_channel.mention}',
                                            color=discord.colour.Color.green())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    await asyncio.sleep(1)
                    embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
                    await interaction.message.edit(embed=embed, view=MyView(bot=self.bot))
                else:
                    embed = discord.Embed(title=f"You already have a open Ticket", color=0xff0000)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    await asyncio.sleep(1)
                    embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
                    await interaction.message.edit(embed=embed, view=MyView(bot=self.bot))
        return

#First Button for the Ticket 
class CloseButton(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket 🎫", style = discord.ButtonStyle.blurple, custom_id="close")
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        ticket_creator = int(interaction.channel.topic)
        cur.execute("SELECT id FROM ticket WHERE discord_id=?", (ticket_creator,))
        ticket_number = cur.fetchone()
        embed = discord.Embed(title="Ticket Closed 🎫", description="Press Reopen to open the Ticket again or Delete to delete the Ticket!", color=discord.colour.Color.green())
        ticket_creator = guild.get_member(ticket_creator)
        await interaction.channel.set_permissions(ticket_creator, send_messages=False, read_messages=False, add_reactions=False,
                                                        embed_links=False, attach_files=False, read_message_history=False,
                                                        external_emojis=False)
        await interaction.channel.edit(name=f"ticket-closed-{ticket_number}")
        await interaction.response.send_message(embed=embed, view=TicketOptions(bot=self.bot))
        button.disabled = True
        await interaction.message.edit(view=self)

def convert_time_to_timestamp(timestamp):
    timestamp_str = timestamp[0]

    datetime_obj = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    discord_timestamp = int(datetime_obj.timestamp())
    return discord_timestamp


#Buttons to reopen or delete the Ticket
class TicketOptions(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @discord.ui.button(label="Reopen Ticket 🎫", style = discord.ButtonStyle.green, custom_id="reopen")
    async def reopen_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        ticket_creator = int(interaction.channel.topic)
        cur.execute("SELECT id FROM ticket WHERE discord_id=?", (ticket_creator,))
        ticket_number = cur.fetchone()        
        embed = discord.Embed(title="Ticket Reopened 🎫", description="Press Delete Ticket to delete the Ticket!", color=discord.colour.Color.green()) #The Embed for the Ticket Channel when it got reopened
        ticket_creator = guild.get_member(ticket_creator)
        await interaction.channel.set_permissions(ticket_creator, send_messages=True, read_messages=True, add_reactions=False,
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=False)
        await interaction.channel.edit(name=f"ticket-{ticket_number}")
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Delete Ticket 🎫", style = discord.ButtonStyle.red, custom_id="delete")
    async def delete_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        channel = self.bot.get_channel(LOG_CHANNEL)
        ticket_creator = int(interaction.channel.topic)

        cur.execute("SELECT ticket_created FROM ticket WHERE discord_id=?", (ticket_creator,))
        ticket_created = cur.fetchone()
        discord_timestamp = convert_time_to_timestamp(ticket_created)

        cur.execute("DELETE FROM ticket WHERE discord_id=?", (ticket_creator,))
        conn.commit()

        military_time: bool = True
        transcript = await chat_exporter.export(
            interaction.channel,
            limit=200,
            tz_info=TIMEZONE,
            military_time=military_time,
            bot=self.bot,
        )       
        if transcript is None:
            return
        
        transcript_file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{interaction.channel.name}.html")
        transcript_file2 = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{interaction.channel.name}.html")
        
        ticket_creator = guild.get_member(ticket_creator)
        embed = discord.Embed(description=f'Ticket is deliting in 5 seconds.', color=0xff0000)
        transcript_info = discord.Embed(title=f"Ticket Deleting | {interaction.channel.name}", description=f"Ticket from: {ticket_creator.mention}\nTicket Name: {interaction.channel.name}\n Ticket Created at: <t:{discord_timestamp}:F> \n Closed from: {interaction.user.mention}", color=discord.colour.Color.blue())

        await interaction.response.send_message(embed=embed)
        await ticket_creator.send(embed=transcript_info, file=transcript_file)
        await channel.send(embed=transcript_info, file=transcript_file2)
        await asyncio.sleep(3)
        await interaction.channel.delete(reason="Ticket got Deleted!")