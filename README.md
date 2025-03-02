# 🚀 Boot-Img-Bot - Discord Image Resizer Bot

Boot-Img-Bot is a Discord bot that allows users to resize images directly in a Discord server. This bot is hosted on a Raspberry Pi and runs using `supervisor` for automatic startup and process management.

---

## 📌 Features
- Resizes images and GIFs uploaded to Discord for boot image use on M5 Bruce devices.
- Supports multiple resolutions:
  - **M5Stick & Cardputer**: 240x135
  - **T-Embed CC1101**: 320x170
  - **CYD**: 320x240
- Runs on a Raspberry Pi
- Automatically restarts with `supervisor`
- Uses `discord.py` and `Pillow` for image processing

---

👉 **Join my Discord server HackLab to stay updated and get support:**  
🔗 [HackLab Discord Server](https://discord.gg/R8QJKCFYr9)

---

## 🛠️ Setup Instructions (Raspberry Pi)

### ✅ **1️⃣ Install Dependencies**
Before setting up the bot, install the required dependencies:
```sh
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-venv python3-pip supervisor -y
```

### ✅ **2️⃣ Clone the Repository**
```sh
cd ~
git clone https://github.com/your-repo/boot-img-bot.git
cd boot-img-bot
```

### ✅ **3️⃣ Setup Virtual Environment & Install Requirements**
```sh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install asyncio
pip install pillow
pip install aiohttp
pip install python-dotenv
```

### ✅ **4️⃣ Configure Environment Variables**
Create a `.env` file with your Discord bot token:
```sh
nano .env
```
Add the following:
```
DISCORD_TOKEN=your-super-secret-token
```
Save and exit (`CTRL + X`, then `Y`, then `Enter`).

---

## 🔄 Running the Bot

### ✅ **Manually Start the Bot**
```sh
source venv/bin/activate
python bot.py
```

### ✅ **Run in Background with `tmux` (Alternative to Supervisor)**
```sh
tmux new -s discord-bot
source venv/bin/activate
python bot.py
# Detach from tmux session: CTRL + B, then D
```

---

## 🛠️ Supervisor Setup (Auto-Start on Boot)

### ✅ **1️⃣ Create Supervisor Config**
```sh
sudo nano /etc/supervisor/conf.d/discord-bot.conf
```
Paste the following configuration:
```
[program:discord-bot]
command=/home/unveroleone/boot-img-bot/venv/bin/python /home/unveroleone/boot-img-bot/bot.py
directory=/home/unveroleone/boot-img-bot
autostart=true
autorestart=true
stderr_logfile=/var/log/discord-bot.err.log
stdout_logfile=/var/log/discord-bot.out.log
user=unveroleone
numprocs=1
```
Save and exit (`CTRL + X`, then `Y`, then `Enter`).

### ✅ **2️⃣ Reload & Start Supervisor**
```sh
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start discord-bot
```

### ✅ **3️⃣ Check Bot Status**
```sh
sudo supervisorctl status discord-bot
```

### ✅ **4️⃣ Restart the Bot**
```sh
sudo supervisorctl restart discord-bot
```

---

## 🛠️ Debugging & Logs

### ✅ **Check Logs**
```sh
cat /var/log/discord-bot.out.log  # Normal logs
cat /var/log/discord-bot.err.log  # Error logs
```

### ✅ **Kill All Running Bot Processes (If Needed)**
```sh
ps aux | grep python
pkill -f bot.py
```

---

## 🎯 Notes
- Make sure `supervisor` is enabled on boot:
  ```sh
  sudo systemctl enable supervisor
  ```
- If running manually with `tmux`, ensure you **detach** properly so the bot keeps running.

🚀 **Now your Discord bot is fully set up and running on your Raspberry Pi!**

