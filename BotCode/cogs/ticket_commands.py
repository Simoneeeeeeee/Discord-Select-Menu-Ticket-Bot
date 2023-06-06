import discord
import json
from discord import *
from discord.ext import commands
from discord.ext.commands import has_permissions
from cogs.ticket_system import MyView

with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

TICKET_CHANNEL = config["ticket_channel_id"] #Where the bot should send the Embed + SelectMenu

class Ticket_Command(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot Loaded | ticket_commands.py ✅')


        #Slash Command to show the Ticket Menu in the Ticket Channel
    @commands.slash_command(name="ticket")
    @has_permissions(administrator=True)
    async def ticket(self, ctx):
        self.channel = self.bot.get_channel(TICKET_CHANNEL)
        self.embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
        await self.channel.send(embed=self.embed, view=MyView(bot=self.bot))
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
