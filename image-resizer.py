import discord
from discord.ext import commands
from PIL import Image
import aiohttp
import io
from dotenv import load_dotenv
import os

# Insert your bot token here
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Bot intents for messages and file processing
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.typing = False
intents.presences = False
intents.message_content = True  # Required to detect messages with images

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user.name}')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself to prevent loops
    if message.author == bot.user:
        return

    # Check if there are any attachments in the message
    if message.attachments:
        for attachment in message.attachments:
            # Check if the attachment is a JPG or GIF image
            if attachment.filename.lower().endswith(('.jpg', '.jpeg', '.gif')):
                await message.channel.send("Processing your image...")

                # Download the image
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp:
                        if resp.status != 200:
                            await message.channel.send("Error downloading the file.")
                            return

                        img_data = await resp.read()

                # Open and resize the image
                try:
                    with Image.open(io.BytesIO(img_data)) as img:
                        # Ensure the image format is valid
                        image_format = img.format if img.format else "JPEG"
                        file_extension = "jpg" if image_format.lower() == "jpeg" else image_format.lower()
                        new_filename = f"boot.{file_extension}"

                        img = img.resize((240, 135))  # Resize image to 240x135

                        # Save the resized image
                        output_buffer = io.BytesIO()
                        img.save(output_buffer, format=image_format)
                        output_buffer.seek(0)

                        # Send the resized image back to Discord
                        await message.channel.send("Here is your resized image:", file=discord.File(output_buffer, filename=new_filename))

                except Exception as e:
                    await message.channel.send("There was an error processing the image.")
                    print(f"Error: {e}")
            else:
                await message.channel.send("Only JPG and GIF files are supported.")

    await bot.process_commands(message)

bot.run(TOKEN)