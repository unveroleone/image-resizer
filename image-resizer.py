import discord
from discord.ext import commands
from PIL import Image
import aiohttp
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Bot intents for messages and file processing
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.reactions = True  # Needed for reaction tracking!
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

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user.name}')

@bot.command()
async def resizer(ctx):
    """Sends an embed message with the size options."""
    embed = discord.Embed(
        title="🖼️ Image Resizer",
        description="React with the correct emoji to choose a device format.",
        color=discord.Color.blue()
    )
    embed.add_field(name="📟 M5Stick / Cardputer", value="240x135", inline=False)
    embed.add_field(name="📡 T-Embed CC1101", value="320x170", inline=False)
    embed.add_field(name="🖥️ CYD", value="320x240", inline=False)
    
    message = await ctx.send(embed=embed)

    # Add reaction options
    for emoji in size_options.keys():
        await message.add_reaction(emoji)

    # Store the message ID so we can track reactions
    bot.embed_message_id = message.id

@bot.event
async def on_reaction_add(reaction, user):
    """Triggered when a user reacts to the embed."""
    if user.bot:
        return

    # Ensure reaction is on the correct embed message
    if reaction.message.id != getattr(bot, "embed_message_id", None):
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

            # Wenn das Bild ein animiertes GIF ist
            if img.format == "GIF" and getattr(img, "is_animated", False):
                frames = []
                for frame in range(img.n_frames):
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
                new_filename = "boot.gif"
            else:
                # Für nicht-animierte Bilder
                img = img.resize(size, Image.LANCZOS)
                output_buffer = io.BytesIO()
                img.save(output_buffer, format=image_format)
                output_buffer.seek(0)
                new_filename = f"boot.{file_extension}"

            file = discord.File(output_buffer, filename=new_filename)
            await user.send(f"✅ Here is your resized image ({size[0]}x{size[1]}).", file=file)

    except Exception as e:
        await user.send("⚠️ There was an error processing the image.")
        print(f"Error: {e}")

# Start the bot
bot.run(TOKEN)
