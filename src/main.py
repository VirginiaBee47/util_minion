import discord
from discord.ext import commands

from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase
from datetime import datetime

from secret import API_KEY, GUILD_ID
from db_io import schedule_single_event, save_discussion_topic, load_discussion_topics, delete_discussion_topic
from util import hash

GUILD = discord.Object(id=GUILD_ID)

class BotClient(commands.Bot):
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self.database = None

    async def on_ready(self):
        print(f'Logged in as {self.user.name} - {self.user.id}')
        print('------')

        try:
            guild = discord.Object(id=1362588939663446057)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to the guild {guild.id}.')
        except Exception as e:
            print(f'Failed to sync commands: {e}')

    async def on_message(self, message):
        print(f'Received message from {message.author.name}: {message.content}')
        return await super().on_message(message)
            
    
intents = discord.Intents.all()
intents.message_content = True  # Enable message intents
bot = BotClient(command_prefix='!', intents=intents)

@bot.tree.command(name='ping', description='Play a fun little ping pong game.', guild=GUILD)
async def ping(ctx: discord.Interaction):
    await ctx.response.send_message('Pong!')

@bot.tree.command(name='log', description='Log an item in a specific category.', guild=GUILD)
async def log(ctx: discord.Interaction, category: str, item: str):
    if category is None and item is None:
        await ctx.response.send_message("Please provide both category and item arguments.")
        return
    elif category is None:
        await ctx.response.send_message("Please provide a category argument.")
        return
    elif item is None:
        await ctx.response.send_message("Please provide an item argument.")
        return
    else:
        category = category.strip().upper()
        item = item.strip().upper()
        await ctx.response.send_message(f"This will work eventually, lmao. {category} - {item}")

"""
@bot.tree.command(name='schedule', description='Schedule a single event.', guild=GUILD)
async def schedule(ctx: discord.Interaction, event_name: str, start_datetime: str, end_datetime: str, description: str = None, location: str = None, attendees: str = None):
    try:
        post_id = schedule_single_event(db = bot.database, 
                                        name=event_name, 
                                        author=ctx.user.name, 
                                        start_datetime=start_datetime, 
                                        end_datetime=end_datetime, 
                                        description=description, 
                                        location=location, 
                                        attendees=attendees)
        await ctx.response.send_message(f"Event '{event_name}' scheduled successfully!\nPost ID: {post_id}")
    except Exception as e:
        await ctx.response.send_message(f"Failed to schedule event: {e}")
"""

@bot.tree.command(name='pin', description='Pin a topic of discussion.', guild=GUILD)
async def pin(ctx: discord.Interaction, topic: str):
    try:
        save_discussion_topic(topic=topic,
                              author=ctx.user.name,
                              date=datetime.now(),
                              channel_id=ctx.channel.id)
        await ctx.response.send_message(f"Channel id: {ctx.channel.id}\nTopic: {topic}\nPin time: {datetime.now()}\nAuthor: {ctx.user.name}")
    except Exception as e:
        await ctx.response.send_message(f"Failed to pin topic: {e}")

@bot.tree.command(name='unpin', description='Unpin a topic of discussion.', guild=GUILD)
async def unpin(ctx: discord.Interaction, topic: str):
    try:
        delete_discussion_topic(topic=topic, channel_id=ctx.channel.id)
        await ctx.response.send_message(f"Topic '{topic}' unpinned successfully.")
    except Exception as e:
        await ctx.response.send_message(f"Failed to unpin topic: {e}")

@bot.tree.command(name='recall', description='Recall a topic of discussion.', guild=GUILD)
async def recall(ctx: discord.Interaction, author: str = None):
    try:
        pins = load_discussion_topics(channel_id=ctx.channel.id)
        topics = []
        authors = []
        times = []

        for pin in pins:
            print("pin:", pin)
            if author and not pin[0].startswith(author.strip().upper()):
                continue
            authors.append(pin[1].strip())
            topics.append(pin[0].strip())
            times.append(pin[2].strip())

        pin_strings = [author + " "*(len(max(authors, key=len)) - len(author)) + "   |   **" + topic + "**" + " "*(len(max(topics, key=len)) - len(topic)) + "   |   " + time for author, topic, time in zip(authors, topics, times)]
        print("pin_strings:", pin_strings)
        await ctx.response.send_message("Pinned topics of discussion in this channel\n-------------------------------------------\n" + "\n".join(pin_strings))
    except Exception as e:               
        await ctx.response.send_message(f"Failed to recall topic: {e}")

def main():
    client = MongoClient("mongodb://localhost:27017/")
    db = client.bot_facing_db

    bot.database = db
    bot.run(API_KEY)

if __name__ == "__main__":
    main()