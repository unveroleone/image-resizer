import discord
from discord.ext import commands
from PIL import Image
import aiohttp
import io
import os
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Channel ID where the bot will send messages
CHANNEL_ID = 1334922393990336631

# Bot intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)

# Size options for different devices
size_options = {
    "📟": (240, 135),  # M5Stick & Cardputer
    "📡": (320, 170),  # T-Embed CC1101
    "🖥️": (320, 240)   # CYD
}

# File for storing the embed message ID
EMBED_MESSAGE_FILE = "embed_message.json"

def save_embed_message_id(message_id):
    """Saves the embed message ID to a JSON file."""
    with open(EMBED_MESSAGE_FILE, "w") as f:
        json.dump({"embed_message_id": message_id}, f)

def load_embed_message_id():
    """Loads the stored message ID."""
    try:
        with open(EMBED_MESSAGE_FILE, "r") as f:
            data = json.load(f)
            return data.get("embed_message_id")
    except (FileNotFoundError, json.JSONDecodeError):
        return None

async def delete_old_embed():
    """Deletes the old embed message if it still exists."""
    embed_message_id = load_embed_message_id()
    if not embed_message_id:
        return

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("⚠️ The bot does not have access to the channel.")
        return

    try:
        old_message = await channel.fetch_message(embed_message_id)
        await old_message.delete()
        print(f"🗑️ Old embed message deleted (ID: {embed_message_id})")
    except discord.NotFound:
        print("⚠️ The old message was already deleted.")
    except discord.Forbidden:
        print("❌ The bot does not have permission to delete messages!")

async def send_new_embed():
    """Sends a new embed message on every restart."""
    await delete_old_embed()
    
    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        print("⚠️ Bot cannot find the channel. Check the CHANNEL_ID.")
        return

    embed = discord.Embed(
        title="🖼️ Image Resizer",
        description="React with the correct emoji to choose a device format.",
        color=discord.Color.blue()
    )
    embed.add_field(name="📟 M5Stick / Cardputer", value="240x135", inline=False)
    embed.add_field(name="📡 T-Embed CC1101", value="320x170", inline=False)
    embed.add_field(name="🖥️ CYD", value="320x240", inline=False)

    message = await channel.send(embed=embed)
    for emoji in size_options.keys():
        await message.add_reaction(emoji)

    bot.embed_message_id = message.id
    save_embed_message_id(message.id)
    print(f"✅ New embed message sent in {channel.name} (ID: {message.id})")

@bot.event
async def on_ready():
    """Starts the bot and sends a new embed message."""
    print(f'✅ Bot is online as {bot.user.name}')
    await send_new_embed()

@bot.event
async def on_reaction_add(reaction, user):
    """Triggered when a user reacts to the embed."""
    if user.bot:
        return

    embed_message_id = bot.embed_message_id
    if reaction.message.id != embed_message_id:
        return

    if reaction.emoji in size_options:
        size = size_options[reaction.emoji]
        await user.send(f"📥 Please upload an image to be resized to **{size[0]}x{size[1]}**.")

        def check(msg):
            return msg.author == user and msg.attachments

        try:
            msg = await bot.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            await user.send("⏳ Timed out! Please react again and upload the image faster.")
            return

        if msg.attachments:
            image_url = msg.attachments[0].url
            await process_and_send_image(image_url, size, user)

async def process_and_send_image(image_url, size, user):
    """Downloads, resizes, and sends back the processed image while preserving GIF animations."""
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            if resp.status != 200:
                return await user.send("⚠️ There was an error downloading the image.")

            image_bytes = await resp.read()

    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            image_format = img.format if img.format else "JPEG"
            file_extension = image_format.lower() if image_format else "jpg"

            if img.format == "GIF" and getattr(img, "is_animated", False):
                frames = []
                for frame in range(min(img.n_frames, 50)):  # Limit to 50 frames (memory efficiency)
                    img.seek(frame)
                    frame_resized = img.copy().resize(size, Image.NEAREST)
                    frames.append(frame_resized)

                output_buffer = io.BytesIO()
                frames[0].save(
                    output_buffer,
                    format="GIF",
                    save_all=True,
                    append_images=frames[1:],
                    duration=img.info.get("duration", 100),
                    loop=img.info.get("loop", 0)
                )
                output_buffer.seek(0)
                new_filename = "resized.gif"
            else:
                img = img.resize(size, Image.LANCZOS)
                output_buffer = io.BytesIO()
                img.save(output_buffer, format=image_format)
                output_buffer.seek(0)
                new_filename = f"resized.{file_extension}"

            file = discord.File(output_buffer, filename=new_filename)
            await user.send(f"Here is your resized image ({size[0]}x{size[1]}).", file=file)

    except Exception as e:
        await user.send("⚠️ There was an error processing the image.")
        print(f"Error: {e}")

bot.run(TOKEN)
