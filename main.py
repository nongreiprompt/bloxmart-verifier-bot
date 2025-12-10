import os
import discord
from discord.ext import commands

# === CONFIGURASI ===
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("❌ DISCORD_TOKEN belum diatur! Cek Railway environment variables.")

# Channel IDs
INTRO_CHANNEL_ID = 1448237276642410589    # 📰︱ruang-interogasi
CHANGE_NAME_CHANNEL_ID = 1448292386932527156  # 👨︱ganti-username
CHAT_CHANNEL_ID = 1447842346183168062    # 💬︱obrolan-santai

# Role Names
UNVERIFIED_ROLE_NAME = "Unverified"
VERIFIED_ROLE_NAME = "Member"

# Setup bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot {bot.user} berhasil online!")
    print(f"📡 Terhubung ke {len(bot.guilds)} server")

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

    guild = message.guild
    member = message.author

    # Verifikasi otomatis (user baru)
    if message.channel.id == INTRO_CHANNEL_ID:
        await handle_verification(message, guild, member, is_new_user=True)
    
    # Ganti username manual (user lama/semua user)
    elif message.channel.id == CHANGE_NAME_CHANNEL_ID:
        await handle_verification(message, guild, member, is_new_user=False)

    await bot.process_commands(message)

async def handle_verification(message, guild, member, is_new_user):
    roblox_name = message.content.strip()
    
    # Validasi input
    if len(roblox_name) < 3 or " " in roblox_name or not roblox_name.replace("_", "").isalnum():
        await message.channel.send("❌ Format tidak valid! Gunakan huruf, angka, atau underscore. Contoh: `olive`")
        return

    try:
        # Ganti nickname
        new_nick = f"{member.name} - {roblox_name}"
        await member.edit(nick=new_nick)
        
        # Kelola role
        verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
        unverified_role = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE_NAME)
        
        if unverified_role:
            await member.remove_roles(unverified_role)
        if verified_role and verified_role not in member.roles:
            await member.add_roles(verified_role)
        
        # Kirim pesan konfirmasi
        chat_channel = bot.get_channel(CHAT_CHANNEL_ID)
        if is_new_user:
            await message.channel.send(
                f"✅ Terima kasih, {member.mention}!\n"
                f"Selamat bergabung di server kami! 🎉\n"
                f"Silakan lanjut ke: {chat_channel.mention} untuk ngobrol santai!"
            )
        else:
            await message.channel.send(
                f"Hai {member.mention}, nickname kamu sekarang: **{new_nick}**! 🎉\n"
                f"Kamu sudah resmi jadi member! Yuk ngobrol di: {chat_channel.mention}"
            )
        
        print(f"✅ {member} diverifikasi sebagai: {roblox_name}")
        
    except discord.Forbidden:
        await message.channel.send("❌ Bot tidak punya izin untuk mengubah nickname atau role!")
    except Exception as e:
        await message.channel.send("⚠️ Terjadi kesalahan. Hubungi admin.")
        print(f"Error: {e}")

# Jalankan bot
bot.run(TOKEN)
