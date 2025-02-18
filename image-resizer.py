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
intents.guilds = True
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix="!", intents=intents)

# Size options for different devices
size_options = {
    "📟": (240, 135),  # M5Stick & Cardputer
    "📡": (320, 240),  # T-Embed CC1101
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
    embed.add_field(name="📡 T-Embed CC1101", value="320x240", inline=False)
    embed.add_field(name="🖥️ CYD", value="320x240", inline=False)
    
    message = await ctx.send(embed=embed)

    # Add reaction options
    for emoji in size_options.keys():
        await message.add_reaction(emoji)

@bot.event
async def on_reaction_add(reaction, user):
    """Triggered when a user reacts to the embed."""
    if user.bot:
        return

    if reaction.emoji in size_options:
        size = size_options[reaction.emoji]
        await reaction.message.channel.send(
            f"{user.mention}, please upload the image you want to resize to **{size[0]}x{size[1]}**.",
            ephemeral=True  # Message is only visible to the user
        )

        def check(msg):
            return msg.author == user and msg.attachments
        
        msg = await bot.wait_for("message", check=check)
        if msg.attachments:
            image_url = msg.attachments[0].url
            await process_and_send_image(image_url, size, user, reaction.message.channel)

async def process_and_send_image(image_url, size, user, channel):
    """Downloads, resizes, and sends back the processed image as 'boot.[format]'."""
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as resp:
            if resp.status != 200:
                return await channel.send(f"{user.mention}, there was an error downloading the image.", ephemeral=True)
            
            image_bytes = await resp.read()
    
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            image_format = img.format if img.format else "JPEG"
            file_extension = "jpg" if image_format.lower() == "jpeg" else image_format.lower()
            
            # Convert PNG to JPG
            if file_extension == "png":
                img = img.convert("RGBA")
                white_bg = Image.new("RGB", img.size, (255, 255, 255))
                white_bg.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                img = white_bg  # Replace with new image
                file_extension = "jpg"
                image_format = "JPEG"

            # Set the filename to "boot.[format]"
            new_filename = f"boot.{file_extension}"

            img = img.resize(size, Image.ANTIALIAS)

            output_buffer = io.BytesIO()
            img.save(output_buffer, format=image_format)
            output_buffer.seek(0)

            file = discord.File(output_buffer, filename=new_filename)
            await channel.send(f"{user.mention}, here is your resized image ({size[0]}x{size[1]}).", file=file, ephemeral=True)

    except Exception as e:
        await channel.send(f"{user.mention}, there was an error processing the image.", ephemeral=True)
        print(f"Error: {e}")

# Start the bot
bot.run(TOKEN)
