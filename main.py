#Version: 1.6
#GitHub: https://github.com/Simoneeeeeeee/Discord-Select-Menu-Ticket-Bot
#Discord: discord.gg/ycZDpat7dB

import discord
import asyncio
import json
from discord import *
from discord.ui import *
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from discord.ui.item import Item
from pytz import timezone

with open("config.json", mode="r") as config_file:
    config = json.load(config_file)

BOT_TOKEN = config["token"]  #Bot Token create bot on discord.dev

GUILD_ID = config["guild_id"] #Server ID
TICKET_CHANNEL = config["ticket_channel_id"] #Where the bot should send the Embed + SelectMenu

CATEGORY_ID1 = config["category_id_1"] #Support1 Category ID
CATEGORY_ID2 = config["category_id_2"] #Support2 Category ID

TEAM_ROLE1 = config["team_role_id_1"] #Permissions for Support1
TEAM_ROLE2 = config["team_role_id_2"] #Permissions for Support2

LOG_CHANNEL = config["log_channel_id"] #Log Channel ID
TIMEZONE = config["timezone"] #Timezone for the Log you find all timezones at https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568

bot = commands.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f"Bot Online | {bot.user.name}")
    bot.add_view(MyView())
    bot.add_view(Close())
    bot.add_view(TicketOptions())
    richpresence.start()

#Bot Status, Counting all opened Tickets in the Server. You need to add/change things if you have more or less than 2 Categories
@tasks.loop(minutes=1)
async def richpresence():
    guild = bot.get_guild(GUILD_ID)
    category1 = discord.utils.get(guild.categories, id=int(CATEGORY_ID1))
    category2 = discord.utils.get(guild.categories, id=int(CATEGORY_ID2))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'Tickets | {len(category1.channels) + len(category2.channels)}'))


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
                    if f"ticket-{str(interaction.user.id)}" in ticket.name:
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
                embed = discord.Embed(description=f'Welcome {interaction.user.mention},\n'
                                                   'describe your Problem and our Support will help you soon.',
                                                color=discord.colour.Color.blue())
                await ticket_channel.send(embed=embed, view=Close())

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
                    if f"ticket-{str(interaction.user.id)}" in ticket.name:
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
                embed = discord.Embed(description=f'Welcome {interaction.user.mention},\n'
                                                   'describe your Problem and our Support will help you soon.',
                                                    color=discord.colour.Color.blue())
                await ticket_channel.send(embed=embed, view=Close())

                embed = discord.Embed(description=f'📬 Ticket was Created! Look here --> {ticket_channel.mention}',
                                        color=discord.colour.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True)

                await asyncio.sleep(3)
                embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
                await interaction.message.edit(embed=embed, view=MyView())
        return

#First Button for the Ticket 
class Close(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket 🎫", style = discord.ButtonStyle.blurple, custom_id="close")
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = bot.get_guild(GUILD_ID)
        ticket_creator = guild.get_member(int(interaction.channel.topic))
        await interaction.channel.set_permissions(ticket_creator, send_messages=False, read_messages=False, add_reactions=False,
                                                        embed_links=False, attach_files=False, read_message_history=False,
                                                        external_emojis=False)
        await interaction.channel.edit(name=f"closed-{interaction.channel.topic}")
        user_embed = discord.Embed(title="Ticket Closed 🎫", description="DM an Moderator to reopen the Ticket, if it got closed by accident!", color=discord.colour.Color.red())
        embed = discord.Embed(title="Ticket Closed 🎫", description="Press Reopen to open the Ticket again or Delete to delete the Ticket!", color=discord.colour.Color.green())
        await ticket_creator.send(embed=user_embed)
        button.disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.send_message(embed=embed, view=TicketOptions())


#Buttons to reopen or delete the Ticket
class TicketOptions(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Reopen Ticket 🎫", style = discord.ButtonStyle.green, custom_id="reopen")
    async def reopen(self, button: discord.ui.Button, interaction: discord.Interaction):
        guild = bot.get_guild(GUILD_ID)
        ticket_creator = guild.get_member(int(interaction.channel.topic))
        await interaction.channel.set_permissions(ticket_creator, send_messages=True, read_messages=True, add_reactions=False,
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=False)
        await interaction.channel.edit(name=f"ticket-{interaction.channel.topic}")
        user_embed = discord.Embed(title="Ticket Reopened 🎫", description="Your Ticket got reopened!", color=discord.colour.Color.green()) #The Embed the User gets when the Ticket got reopened
        embed = discord.Embed(title="Ticket Reopened 🎫", description="Press Delete Ticket to delete the Ticket!", color=discord.colour.Color.green()) #The Embed for the Ticket Channel when it got reopened
        await ticket_creator.send(embed=user_embed)
        await interaction.response.send_message(embed=embed)

    @discord.ui.button(label="Delete Ticket 🎫", style = discord.ButtonStyle.red, custom_id="delete")
    async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        channel = bot.get_channel(LOG_CHANNEL)
        guild = bot.get_guild(GUILD_ID)
        ticket_creator = guild.get_member(int(interaction.channel.topic))

        fileName = f"{interaction.channel.name}.txt"
        with open(fileName, "w", encoding='utf-8') as file:
            async for msg in interaction.channel.history(limit=None, oldest_first=True):
                time = msg.created_at.replace(tzinfo=timezone('UTC')).astimezone(timezone(TIMEZONE))
                file.write(f"{time} - {msg.author.display_name}: {msg.clean_content}\n")

        embed = discord.Embed(description=f'Ticket is closing in 5 seconds.', color=0xff0000)
        embed2 = discord.Embed(title="Ticket Closed!", description=f"Ticket Name: {interaction.channel.name}\n Ticket from: <@{interaction.channel.topic}>\n Closed from: {interaction.user.name}\n Transcript: ", color=discord.colour.Color.blue())
        file = discord.File(fileName)
        embed_for_creator = discord.Embed(title="Your Ticket got Deleted!", color=discord.colour.Color.red())

        await interaction.response.send_message(embed=embed)
        await ticket_creator.send(embed=embed_for_creator)
        await asyncio.sleep(1)
        await channel.send(embed=embed2)
        await channel.send(file=file)
        await asyncio.sleep(1)
        await interaction.channel.delete(reason="Ticket got Deleted!")


#Slash Command to show the Ticket Menu in the Ticket Channel
@bot.slash_command(name="ticket")
@has_permissions(administrator=True)
async def ticket(ctx):
    channel = bot.get_channel(TICKET_CHANNEL)
    embed = discord.Embed(title="Support-Tickets", color=discord.colour.Color.blue())
    await channel.send(embed=embed, view=MyView())
    await ctx.respond("Ticket Menu was send!", ephemeral=True)

#Slash Command to delete the Ticket
@bot.slash_command(name="delete", description="Delete a Ticket instantly!")
async def delete(ctx):
    if "ticket-" in ctx.channel.name or "closed-" in ctx.channel.name:
        channel = bot.get_channel(LOG_CHANNEL)

        fileName = f"{ctx.channel.name}.txt"
        with open(fileName, "w", encoding='utf-8') as file:
            async for msg in ctx.channel.history(limit=None, oldest_first=True):
                time = msg.created_at.replace(tzinfo=timezone('UTC')).astimezone(timezone(TIMEZONE))
                file.write(f"{time} - {msg.author.display_name}: {msg.clean_content}\n")

        embed = discord.Embed(description=f'Ticket is closing in 5 seconds.', color=0xff0000)
        embed2 = discord.Embed(title="Ticket Closed!", description=f"Ticket Name: {ctx.channel.name}\n Ticket from: <@{ctx.channel.topic}>\n Closed from: {ctx.author.name}\n Transcript: ", color=discord.colour.Color.blue())
        file = discord.File(fileName)
        await ctx.respond(embed=embed)
        await channel.send(embed=embed2)
        await channel.send(file=file)
        await asyncio.sleep(1)
        await ctx.channel.delete(reason="Ticket got Deleted!")
    else:
        embed = discord.Embed(description=f'You can only use this command in a Ticket!', color=discord.colour.Color.red())
        await ctx.respond(embed=embed)

#Slash Command to add Members to the Ticket
@bot.slash_command(name="add", description="Add a Member from the Ticket")
async def add(ctx, member: Option(discord.Member, description="Which Member you want to add from the Ticket", required = True)):
    if "ticket-" in ctx.channel.name or "closed-" in ctx.channel.name:
        await ctx.channel.set_permissions(member, send_messages=True, read_messages=True, add_reactions=False,
                                            embed_links=True, attach_files=True, read_message_history=True,
                                            external_emojis=True)
        embed = discord.Embed(description=f'Added {member.mention} to this Ticket <#{ctx.channel.id}>! \n Use /remove to remove a User.', color=discord.colour.Color.green())
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(description=f'You can only use this command in a Ticket!', color=discord.colour.Color.red())
        await ctx.respond(embed=embed)

#Slash Command to remove Members from the Ticket
@bot.slash_command(name="remove", description="Remove a Member from the Ticket")
async def remove(ctx, member: Option(discord.Member, description="Which Member you want to remove from the Ticket", required = True)):
    if "ticket-" in ctx.channel.name or "closed-" in ctx.channel.name:
        await ctx.channel.set_permissions(member, send_messages=False, read_messages=False, add_reactions=False,
                                            embed_links=False, attach_files=False, read_message_history=False,
                                            external_emojis=False)
        embed = discord.Embed(description=f'Removed {member.mention} from this Ticket <#{ctx.channel.id}>! \n Use /add to add a User.', color=discord.colour.Color.green())
        await ctx.respond(embed=embed)
    else:
        embed = discord.Embed(description=f'You can only use this command in a Ticket!', color=discord.colour.Color.red())
        await ctx.respond(embed=embed)

bot.run(BOT_TOKEN)
