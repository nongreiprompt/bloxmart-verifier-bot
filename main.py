import os
import discord
from discord.ext import commands

# === CONFIG ===
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ DISCORD_TOKEN belum diatur!")

INTRO_CHANNEL_ID = 1448237276642410589  # 📰︱ruang-interogasi
CHAT_CHANNEL_ID = 1447842346183168062    # 💬︱obrolan-santai

UNVERIFIED_ROLE_NAME = "Unverified"
VERIFIED_ROLE_NAME = "Member"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} online!")

@bot.event
async def on_member_join(member):
    guild = member.guild
    unverified_role = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE_NAME)
    if unverified_role:
        await member.add_roles(unverified_role)
        intro_channel = bot.get_channel(INTRO_CHANNEL_ID)
        if intro_channel:
            await intro_channel.send(
                f"Hai {member.mention}! 🎮\n"
                f"Silakan masukkan **username Roblox** kamu di sini.\n"
                f"Contoh: ketik `rinanti`"
            )

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id == INTRO_CHANNEL_ID:
        roblox_name = message.content.strip()
        
        if len(roblox_name) < 3 or " " in roblox_name or not roblox_name.replace("_", "").isalnum():
            await message.channel.send("❌ Format tidak valid! Gunakan huruf, angka, atau underscore. Contoh: `rinanti`")
            return

        try:
            new_nick = f"{message.author.name} - {roblox_name}"
            await message.author.edit(nick=new_nick)
            
            guild = message.guild
            verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
            unverified_role = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE_NAME)
            
            if unverified_role:
                await message.author.remove_roles(unverified_role)
            if verified_role:
                await message.author.add_roles(verified_role)
            
            # ✅ Pesan selamat datang + arahkan ke channel obrolan
            chat_channel = bot.get_channel(CHAT_CHANNEL_ID)
            await message.channel.send(
                f"✅ Terima kasih, {message.author.mention}!\n"
                f"Selamat bergabung di server kami! 🎉\n"
                f"Silakan lanjut ke: {chat_channel.mention} untuk ngobrol santai!"
            )
            
            print(f"✅ {message.author} diverifikasi sebagai: {roblox_name}")
            
        except discord.Forbidden:
            await message.channel.send("❌ Bot tidak punya izin untuk mengubah nickname atau role!")
        except Exception as e:
            await message.channel.send("⚠️ Terjadi kesalahan. Hubungi admin.")
            print(f"Error: {e}")
    
    await bot.process_commands(message)

bot.run(TOKEN)
