import discord
import json
import chat_exporter
import io
import datetime
import sqlite3
from discord import *
from discord.ext import commands
from discord.ext.commands import has_permissions
from cogs.ticket_system import MyView

with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

TICKET_CHANNEL = config["ticket_channel_id"] #Where the bot should send the Embed + SelectMenu
GUILD_ID = config["guild_id"] #Server ID

LOG_CHANNEL = config["log_channel_id"] #Log Channel ID
TIMEZONE = config["timezone"] #Timezone for the Timestamp https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List

conn = sqlite3.connect('user.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS ticket 
           (id INTEGER PRIMARY KEY AUTOINCREMENT, discord_name TEXT, discord_id INTEGER, ticket_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()

class Ticket_Command(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot Loaded | ticket_commands.py ✅')

    @commands.Cog.listener()
    async def on_bot_shutdown():
        cur.close()
        conn.close()


        #Slash Command to show the Ticket Menu in the Ticket Channel
    @commands.slash_command(name="ticket")
    @has_permissions(administrator=True)
    async def ticket(self, ctx):
        self.channel = self.bot.get_channel(TICKET_CHANNEL)
        embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
        await self.channel.send(embed=embed, view=MyView(self.bot))
        await ctx.respond("Ticket Menu was send!", ephemeral=True)

    #Slash Command to add Members to the Ticket
    @commands.slash_command(name="add", description="Add a Member from the Ticket")
    async def add(self, ctx, member: Option(discord.Member, description="Which Member you want to add from the Ticket", required = True)):
        if "ticket-" in ctx.channel.name or "closed-" in ctx.channel.name:
            await ctx.channel.set_permissions(member, send_messages=True, read_messages=True, add_reactions=False,
                                                embed_links=True, attach_files=True, read_message_history=True,
                                                external_emojis=True)
            self.embed = discord.Embed(description=f'Added {member.mention} to this Ticket <#{ctx.channel.id}>! \n Use /remove to remove a User.', color=discord.colour.Color.green())
            await ctx.respond(embed=self.embed)
        else:
            self.embed = discord.Embed(description=f'You can only use this command in a Ticket!', color=discord.colour.Color.red())
            await ctx.respond(embed=self.embed)

    #Slash Command to remove Members from the Ticket
    @commands.slash_command(name="remove", description="Remove a Member from the Ticket")
    async def remove(self, ctx, member: Option(discord.Member, description="Which Member you want to remove from the Ticket", required = True)):
        if "ticket-" in ctx.channel.name or "closed-" in ctx.channel.name:
            await ctx.channel.set_permissions(member, send_messages=False, read_messages=False, add_reactions=False,
                                                embed_links=False, attach_files=False, read_message_history=False,
                                                external_emojis=False)
            self.embed = discord.Embed(description=f'Removed {member.mention} from this Ticket <#{ctx.channel.id}>! \n Use /add to add a User.', color=discord.colour.Color.green())
            await ctx.respond(embed=self.embed)
        else:
            self.embed = discord.Embed(description=f'You can only use this command in a Ticket!', color=discord.colour.Color.red())
            await ctx.respond(embed=self.embed)

    @commands.slash_command(name="delete", description="Delete the Ticket")
    async def close(self, ctx):
        guild = self.bot.get_guild(GUILD_ID)
        channel = self.bot.get_channel(LOG_CHANNEL)
        ticket_creator = int(ctx.channel.topic)

        cur.execute("SELECT ticket_created FROM ticket WHERE discord_id=?", (ticket_creator,))
        ticket_created = cur.fetchone()
        discord_timestamp = convert_time_to_timestamp(ticket_created)

        cur.execute("DELETE FROM ticket WHERE discord_id=?", (ticket_creator,))
        conn.commit()

        military_time: bool = True
        transcript = await chat_exporter.export(
            ctx.channel,
            limit=200,
            tz_info=TIMEZONE,
            military_time=military_time,
            bot=self.bot,
        )       
        if transcript is None:
            return
        
        transcript_file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{ctx.channel.name}.html")
        transcript_file2 = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{ctx.channel.name}.html")
        
        ticket_creator = guild.get_member(ticket_creator)
        embed = discord.Embed(description=f'Ticket is deliting in 5 seconds.', color=0xff0000)
        transcript_info = discord.Embed(title=f"Ticket Deleting | {ctx.channel.name}", description=f"Ticket from: {ticket_creator.mention}\nTicket Name: {ctx.channel.name}\n Ticket Created at: <t:{discord_timestamp}:F> \n Closed from: {ctx.author.mention}", color=discord.colour.Color.blue())

        await ctx.reply(embed=embed)
        try:
            await ticket_creator.send(embed=transcript_info, file=transcript_file)
        except:
            transcript_info.add_field(name="Error", value="Couldn't send the Transcript to the User because he has his DMs disabled!", inline=True)
        await channel.send(embed=transcript_info, file=transcript_file2)
        await asyncio.sleep(3)
        await ctx.channel.delete(reason="Ticket got Deleted!")

def convert_time_to_timestamp(timestamp):
    timestamp_str = timestamp[0]

    datetime_obj = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    discord_timestamp = int(datetime_obj.timestamp())
    return discord_timestamp