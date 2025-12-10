import os
import discord
from discord.ext import commands

# === AMAN: Ambil token dari Environment Variable ===
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError("❌ DISCORD_TOKEN belum diatur! Cek Railway environment variables.")

# === KONFIGURASI BOT ===
INTRO_CHANNEL_NAME = "📰︱ruang-interogasi"
UNVERIFIED_ROLE_NAME = "Unverified"
VERIFIED_ROLE_NAME = "Member"
BOT_MESSAGE = "Hai {mention}! Silakan masukkan **username Roblok** kamu (tanpa @). Contoh: `rinanti`"

# === SETUP INTENTS ===
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} berhasil online!")
    print(f"📡 Connected to {len(bot.guilds)} server(s)")

@bot.event
async def on_member_join(member):
    guild = member.guild
    unverified_role = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE_NAME)
    if unverified_role:
        await member.add_roles(unverified_role)
        intro_channel = discord.utils.get(guild.text_channels, name=INTRO_CHANNEL_NAME)
        if intro_channel:
            await intro_channel.send(BOT_MESSAGE.format(mention=member.mention))
        else:
            print(f"⚠️ Channel '{INTRO_CHANNEL_NAME}' tidak ditemukan di server {guild.name}")
    else:
        print(f"⚠️ Role '{UNVERIFIED_ROLE_NAME}' tidak ditemukan di server {guild.name}")

@bot.event
async def on_message(message):
    # Abaikan pesan bot
    if message.author.bot:
        return

    # Proses hanya di channel verifikasi
    if message.channel.name == INTRO_CHANNEL_NAME:
        roblox_name = message.content.strip()
        
        # Validasi input
        if len(roblox_name) < 3 or " " in roblox_name or not roblox_name.replace("_", "").isalnum():
            await message.channel.send("❌ Format tidak valid! Gunakan huruf, angka, atau underscore. Contoh: `gogon`")
            return

        try:
            # Ganti nickname
            new_nick = f"{message.author.name} - {roblox_name}"
            await message.author.edit(nick=new_nick)
            
            # Kelola role
            guild = message.guild
            verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
            unverified_role = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE_NAME)
            
            if unverified_role:
                await message.author.remove_roles(unverified_role)
            if verified_role:
                await message.author.add_roles(verified_role)
            
            await message.channel.send("✅ Verifikasi berhasil! Selamat datang di server! 🎉")
            print(f"✅ {message.author} diverifikasi sebagai: {roblox_name}")
            
        except discord.Forbidden:
            await message.channel.send("❌ Bot tidak punya izin untuk mengubah nickname atau role!")
        except Exception as e:
            await message.channel.send("⚠️ Terjadi kesalahan. Hubungi admin.")
            print(f"Error: {e}")
    
    await bot.process_commands(message)

# Jalankan bot
bot.run(TOKEN)
