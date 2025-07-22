import discord
import asyncio
import json
from discord.ext import commands, tasks
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils.graph import create_streak_graph
from utils.calendar_img import create_calendar_image

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
STUDY_CHANNEL_ID = int(os.getenv("STUDY_CHANNEL_ID"))
REMINDER_CHANNEL_ID = int(os.getenv("REMINDER_CHANNEL_ID"))
DATA_FILE = os.getenv("DATA_FILE", "study_data.json")
TIMEZONE = pytz.timezone(os.getenv("TIMEZONE", "America/Sao_Paulo"))
GUILD_ID = int(os.getenv("GUILD_ID"))

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

study_data = load_data()
pending_confirmations = {}
confirmation_attempts = {}

def today_str():
    now = datetime.now(TIMEZONE)
    return now.strftime("%Y-%m-%d")

def now_gmt3():
    return datetime.now(TIMEZONE)

def reset_daily_attempts():
    global confirmation_attempts, pending_confirmations
    confirmation_attempts.clear()
    pending_confirmations.clear()

@bot.event
async def on_ready():
    print(f"Bot online as {bot.user}")
    daily_report.start()
    hourly_reminder.start()
    reset_attempts_daily.start()
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(f"Error syncing slash commands: {e}")

@tasks.loop(minutes=1)
async def reset_attempts_daily():
    now = now_gmt3()
    if now.hour == 0 and now.minute == 0:
        reset_daily_attempts()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.channel.type != discord.ChannelType.private and message.channel.id == STUDY_CHANNEL_ID:
        user_id = str(message.author.id)
        today = today_str()
        user_data = study_data.get(user_id, {})
        confirmations = user_data.get("confirmations", {})
        if confirmations.get(today):
            return
        if user_id not in confirmation_attempts or confirmation_attempts[user_id] is None:
            confirmation_attempts[user_id] = 0
        if confirmation_attempts[user_id] >= 3:
            return
        if user_id in pending_confirmations and pending_confirmations[user_id]:
            return

        async def ask_confirmation_multiple():
            pending_confirmations[user_id] = []
            for attempt in range(3):
                if study_data.get(user_id, {}).get("confirmations", {}).get(today):
                    break
                confirm_msg = await message.channel.send(
                    f"{message.author.mention} Did you really study? Confirm with ✅ to register!"
                )
                await confirm_msg.add_reaction("✅")
                pending_confirmations[user_id].append(confirm_msg.id)
                confirmation_attempts[user_id] += 1
                await asyncio.sleep(60)
                if study_data.get(user_id, {}).get("confirmations", {}).get(today):
                    break

        bot.loop.create_task(ask_confirmation_multiple())

    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.channel_id != STUDY_CHANNEL_ID or str(payload.emoji) != "✅":
        return

    user_id = str(payload.user_id)
    today = today_str()
    if user_id not in pending_confirmations or not pending_confirmations[user_id]:
        return
    if payload.message_id not in pending_confirmations[user_id]:
        return

    guild = bot.get_guild(payload.guild_id)
    user = guild.get_member(payload.user_id) if guild else bot.get_user(payload.user_id)
    if user_id not in study_data:
        study_data[user_id] = {
            "confirmations": {},
            "avatar_url": user.avatar.url if user.avatar else "",
            "username": user.name
        }
    study_data[user_id]["confirmations"][today] = True
    study_data[user_id]["avatar_url"] = user.avatar.url if user.avatar else ""
    study_data[user_id]["username"] = user.name
    save_data(study_data)
    pending_confirmations[user_id] = []

@tasks.loop(seconds=60)
async def daily_report():
    now = now_gmt3()
    if now.hour == 0 and now.minute == 0:
        reminder_channel = bot.get_channel(REMINDER_CHANNEL_ID)
        streak_path = create_streak_graph(study_data)
        await reminder_channel.send("🏆 Consecutive study days ranking:", file=discord.File(streak_path))
        calendar_path = await create_calendar_image(study_data, bot)
        await reminder_channel.send("🗓️ Monthly study calendar:", file=discord.File(calendar_path))

@tasks.loop(minutes=1)
async def hourly_reminder():
    now = now_gmt3()
    if 20 <= now.hour <= 23 and now.minute == 0:
        today = today_str()
        reminder_channel = bot.get_channel(REMINDER_CHANNEL_ID)
        if reminder_channel is None:
            return
        guild = reminder_channel.guild
        notified = set()
        for user_id, data in study_data.items():
            member = guild.get_member(int(user_id))
            if member and not data.get("confirmations", {}).get(today):
                if member.id not in notified:
                    try:
                        await reminder_channel.send(
                            f"{member.mention} You haven't registered your study today yet! Reply in the study channel to register."
                        )
                        notified.add(member.id)
                    except Exception as e:
                        print(f"Error notifying {user_id}: {e}")
        for member in guild.members:
            if member.bot:
                continue
            uid = str(member.id)
            if uid not in study_data or not study_data[uid].get("confirmations", {}).get(today):
                if member.id not in notified:
                    try:
                        await reminder_channel.send(
                            f"{member.mention} You haven't registered your study today yet! Reply in the study channel to register."
                        )
                        notified.add(member.id)
                    except Exception as e:
                        print(f"Error notifying {uid}: {e}")

@bot.command(name="ranking")
async def ranking_command(ctx):
    streak_path = create_streak_graph(study_data)
    with open(streak_path, "rb") as img:
        file = discord.File(img, filename="ranking.png")
        await ctx.send("🏆 Consecutive study days ranking:", file=file)

@bot.command(name="calendar")
async def calendar_command(ctx):
    calendar_path = await create_calendar_image(study_data, bot)
    with open(calendar_path, "rb") as img:
        file = discord.File(img, filename="calendar.png")
        await ctx.send("🗓️ Monthly study calendar:", file=file)

from discord import app_commands

class StudyBotTree(app_commands.CommandTree):
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

@app_commands.command(name="ranking", description="Shows the ranking of consecutive study days.")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def slash_ranking(interaction: discord.Interaction):
    streak_path = create_streak_graph(study_data)
    await interaction.response.send_message("🏆 Consecutive study days ranking:", file=discord.File(streak_path))

@app_commands.command(name="calendar", description="Shows the monthly study calendar.")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def slash_calendar(interaction: discord.Interaction):
    calendar_path = await create_calendar_image(study_data, bot)
    await interaction.response.send_message("🗓️ Monthly study calendar:", file=discord.File(calendar_path))

bot.tree.add_command(slash_ranking, guild=discord.Object(id=GUILD_ID))
bot.tree.add_command(slash_calendar, guild=discord.Object(id=GUILD_ID))

if __name__ == "__main__":
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please create a .env file based on .env.example and add your bot token.")
        exit(1)
    bot.run(TOKEN)