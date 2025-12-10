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
    # Cek permissions
    for guild in bot.guilds:
        bot_member = guild.get_member(bot.user.id)
        print(f"🔑 Permissions di {guild.name}: {bot_member.guild_permissions.manage_nicknames}")

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
    
    # Debug: log setiap pesan di channel ganti username
    if message.channel.id == CHANGE_NAME_CHANNEL_ID:
        print(f"📝 Pesan diterima di ganti-username dari {member}: {message.content}")
    
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
        await message.channel.send(
            f"❌ {member.mention} Format tidak valid! Gunakan huruf, angka, atau underscore.\n"
            f"Contoh: `olive` atau `player_123`"
        )
        return
    
    try:
        # Ambil nama asli Discord user (bukan display name)
        discord_name = member.name  # Username asli discord
        
        # Ganti nickname dengan format: NamaAsli - RobloxUsername
        new_nick = f"{discord_name} - {roblox_name}"
        
        print(f"🔄 Mencoba ganti nickname {member} menjadi: {new_nick}")
        
        # Cek apakah bot bisa ganti nickname member ini
        bot_member = guild.get_member(bot.user.id)
        if bot_member.top_role <= member.top_role and guild.owner_id != bot.user.id:
            await message.channel.send(
                f"❌ {member.mention} Bot tidak bisa ganti nickname kamu karena role kamu lebih tinggi dari bot!\n"
                f"Hubungi admin untuk memindahkan role bot lebih tinggi."
            )
            return
        
        # Ganti nickname
        await member.edit(nick=new_nick)
        print(f"✅ Berhasil ganti nickname: {new_nick}")
        
        # Kelola role
        verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
        unverified_role = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE_NAME)
        
        # Hapus role Unverified jika ada
        if unverified_role and unverified_role in member.roles:
            await member.remove_roles(unverified_role)
            print(f"🔓 Role Unverified dihapus dari {member}")
        
        # Tambah role Member jika belum punya
        if verified_role and verified_role not in member.roles:
            await member.add_roles(verified_role)
            print(f"✅ Role Member ditambahkan ke {member}")
        
        # Kirim pesan konfirmasi
        chat_channel = bot.get_channel(CHAT_CHANNEL_ID)
        
        if is_new_user:
            await message.channel.send(
                f"✅ Terima kasih, {member.mention}!\n"
                f"Nickname kamu sekarang: **{new_nick}** 🎉\n"
                f"Selamat bergabung di server kami!\n"
                f"Silakan lanjut ke {chat_channel.mention} untuk ngobrol santai!"
            )
        else:
            await message.channel.send(
                f"✅ Hai {member.mention}!\n"
                f"Nickname kamu berhasil diganti menjadi: **{new_nick}** 🎉\n"
                f"Silakan lanjut ngobrol di {chat_channel.mention}!"
            )
        
        print(f"✅ {member} diverifikasi/diganti sebagai: {roblox_name}")
        
    except discord.Forbidden:
        await message.channel.send(
            f"❌ {member.mention} Bot tidak punya izin untuk mengubah nickname atau role!\n"
            f"Hubungi admin untuk memberikan permission `Manage Nicknames` dan `Manage Roles` ke bot."
        )
        print(f"❌ Permission denied untuk {member}")
        
    except discord.HTTPException as e:
        await message.channel.send(
            f"⚠️ {member.mention} Terjadi kesalahan saat mengubah nickname. Error: {str(e)}"
        )
        print(f"❌ HTTP Error: {e}")
        
    except Exception as e:
        await message.channel.send(
            f"⚠️ {member.mention} Terjadi kesalahan. Hubungi admin."
        )
        print(f"❌ Unexpected Error: {type(e).__name__}: {e}")

# Jalankan bot
bot.run(TOKEN)
