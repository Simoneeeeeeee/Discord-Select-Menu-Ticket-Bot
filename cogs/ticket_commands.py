import discord
import json
import chat_exporter
import io
import pytz
from datetime import datetime
import sqlite3
from discord import *
from discord.ext import commands
from discord.ext.commands import has_permissions
from cogs.ticket_system import MyView

#This will get everything from the config.json file
with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

TICKET_CHANNEL = config["ticket_channel_id"]
GUILD_ID = config["guild_id"]
LOG_CHANNEL = config["log_channel_id"]
TIMEZONE = config["timezone"]
EMBED_TITLE = config["embed_title"]
EMBED_DESCRIPTION = config["embed_description"]

#This will create and connect to the database
conn = sqlite3.connect('Database.db')
cur = conn.cursor()

class Ticket_Command(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot Loaded  | ticket_commands.py ✅')

    @commands.Cog.listener()
    async def on_bot_shutdown():
        cur.close()
        conn.close()

    #Slash Command to show the Ticket Menu in the Ticket Channel only needs to be used once
    @commands.slash_command(name="ticket")
    @has_permissions(administrator=True)
    @commands.guild_only()
    async def ticket(self, ctx):
        self.channel = self.bot.get_channel(TICKET_CHANNEL)
        embed = discord.Embed(title=EMBED_TITLE, description=EMBED_DESCRIPTION, color=discord.colour.Color.blue())
        await self.channel.send(embed=embed, view=MyView(self.bot))
        await ctx.respond("Ticket Menu was send!", ephemeral=True)

    #Slash Command to add Members to the Ticket
    @commands.slash_command(name="add", description="Add a Member to the Ticket")
    async def add(self, ctx, member: Option(discord.Member, description="Which Member you want to add to the Ticket", required = True)):
        if "ticket-" in ctx.channel.name or "ticket-closed-" in ctx.channel.name:
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
        if "ticket-" in ctx.channel.name or "ticket-closed-" in ctx.channel.name:
            await ctx.channel.set_permissions(member, send_messages=False, read_messages=False, add_reactions=False,
                                                embed_links=False, attach_files=False, read_message_history=False,
                                                external_emojis=False)
            self.embed = discord.Embed(description=f'Removed {member.mention} from this Ticket <#{ctx.channel.id}>! \n Use /add to add a User.', color=discord.colour.Color.green())
            await ctx.respond(embed=self.embed)
        else:
            self.embed = discord.Embed(description=f'You can only use this command in a Ticket!', color=discord.colour.Color.red())
            await ctx.respond(embed=self.embed)

    @commands.slash_command(name="delete", description="Delete the Ticket")
    async def delete_ticket(self, ctx):
        guild = self.bot.get_guild(GUILD_ID)
        channel = self.bot.get_channel(LOG_CHANNEL)
        ticket_id = ctx.channel.id

        cur.execute("SELECT id, discord_id, ticket_created FROM ticket WHERE ticket_channel=?", (ticket_id,))
        ticket_data = cur.fetchone()
        id, ticket_creator_id, ticket_created = ticket_data
        ticket_creator = guild.get_member(ticket_creator_id)

        ticket_created_unix = self.convert_to_unix_timestamp(ticket_created)
        timezone = pytz.timezone(TIMEZONE)
        ticket_closed = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
        ticket_closed_unix = self.convert_to_unix_timestamp(ticket_closed)

        #Creating the Transcript
        military_time: bool = True
        transcript = await chat_exporter.export(ctx.channel, limit=200, tz_info=TIMEZONE, military_time=military_time, bot=self.bot)
        
        transcript_file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{ctx.channel.name}.html")
        transcript_file2 = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{ctx.channel.name}.html")
        
        embed = discord.Embed(description=f'Ticket is deleting in 5 seconds.', color=0xff0000)
        transcript_info = discord.Embed(title=f"Ticket Deleted | {ctx.channel.name}", color=discord.colour.Color.blue())
        transcript_info.add_field(name="ID", value=id, inline=True)
        transcript_info.add_field(name="Opened by", value=ticket_creator.mention, inline=True)
        transcript_info.add_field(name="Closed by", value=ctx.author.mention, inline=True)
        transcript_info.add_field(name="Ticket Created", value=f"<t:{ticket_created_unix}:f>", inline=True)
        transcript_info.add_field(name="Ticket Closed", value=f"<t:{ticket_closed_unix}:f>", inline=True)

        await ctx.respond(embed=embed)
        try:
            await ticket_creator.send(embed=transcript_info, file=transcript_file)
        except:
            transcript_info.add_field(name="Error", value="Ticket Creator DM`s are disabled", inline=True)

        await channel.send(embed=transcript_info, file=transcript_file2)
        await asyncio.sleep(3)
        await ctx.channel.delete(reason="Ticket Deleted")
        cur.execute("DELETE FROM ticket WHERE discord_id=?", (ticket_creator_id,))
        conn.commit()

    def convert_to_unix_timestamp(self, date_string):
        date_format = "%Y-%m-%d %H:%M:%S"
        dt_obj = datetime.strptime(date_string, date_format)
        berlin_tz = pytz.timezone('Europe/Berlin')
        dt_obj = berlin_tz.localize(dt_obj)
        dt_obj_utc = dt_obj.astimezone(pytz.utc)
        return int(dt_obj_utc.timestamp())

