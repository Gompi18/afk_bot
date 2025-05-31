import discord
from discord.ext import tasks, commands
import asyncio
import os
from flask import Flask
from threading import Thread

USER_1 = int(os.getenv("USER_1"))
USER_2 = int(os.getenv("USER_2"))

app = Flask('')


@app.route('/')
def home():
    return "Bot is running!"


def run_web():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run_web)
    t.start()


intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

AFK_CHANNEL_ID = 1363598883724333290
MUTE_TIMEOUT = 300

IGNORED_USERS = [USER_1, USER_2]
user_mute_times = {}


@bot.event
async def on_ready():
    print(f'Bot ist online: {bot.user}')
    check_mutes.start()


@tasks.loop(seconds=30)
async def check_mutes():
    print("Bot läuft...")
    for guild in bot.guilds:
        for member in guild.members:
            if member.voice and member.voice.self_mute and member.voice.self_deaf:
                if member.id in IGNORED_USERS:
                    continue

                now = asyncio.get_event_loop().time()
                if member.id not in user_mute_times:
                    user_mute_times[member.id] = now
                elif now - user_mute_times[member.id] >= MUTE_TIMEOUT:
                    afk_channel = guild.get_channel(AFK_CHANNEL_ID)
                    if afk_channel:
                        await member.move_to(afk_channel)
                        print(
                            f"{member.display_name} wurde in den AFK-Channel verschoben."
                        )
                    user_mute_times.pop(member.id, None)
            else:
                user_mute_times.pop(member.id, None)


keep_alive()
bot.run(os.getenv("BOT_TOKEN"))
