import os
import sys
import discord
from discord.ext import commands
import traceback

# === CONFIGURASI ===
try:
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ ERROR: DISCORD_TOKEN tidak ditemukan!")
        sys.exit(1)
    
    print("✅ TOKEN ditemukan, memulai bot...")
    
except Exception as e:
    print(f"❌ ERROR saat load config: {e}")
    traceback.print_exc()
    sys.exit(1)

# Channel IDs
INTRO_CHANNEL_ID = 1448237276642410589    # 📰︱ruang-interogasi
CHANGE_NAME_CHANNEL_ID = 1448292386932527156  # 👨︱ganti-username
CHAT_CHANNEL_ID = 1447842346183168062    # 💬︱obrolan-santai

# Role Names
UNVERIFIED_ROLE_NAME = "Unverified"
VERIFIED_ROLE_NAME = "Member"

# Setup bot
try:
    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True
    intents.guilds = True
    
    bot = commands.Bot(command_prefix="!", intents=intents)
    print("✅ Bot object berhasil dibuat")
    
except Exception as e:
    print(f"❌ ERROR saat setup bot: {e}")
    traceback.print_exc()
    sys.exit(1)

@bot.event
async def on_ready():
    print("=" * 50)
    print(f"✅ Bot {bot.user} berhasil online!")
    print(f"📡 Bot ID: {bot.user.id}")
    print(f"📡 Terhubung ke {len(bot.guilds)} server")
    print("=" * 50)
    
    # Cek permissions di setiap server
    for guild in bot.guilds:
        print(f"\n🏰 Server: {guild.name} (ID: {guild.id})")
        bot_member = guild.get_member(bot.user.id)
        
        if bot_member:
            perms = bot_member.guild_permissions
            print(f"  ✓ Manage Nicknames: {perms.manage_nicknames}")
            print(f"  ✓ Manage Roles: {perms.manage_roles}")
            print(f"  ✓ Read Messages: {perms.read_messages}")
            print(f"  ✓ Send Messages: {perms.send_messages}")
            print(f"  ✓ Bot Role Position: {bot_member.top_role.position}")
        
        # Cek apakah channel ada
        intro_ch = guild.get_channel(INTRO_CHANNEL_ID)
        change_ch = guild.get_channel(CHANGE_NAME_CHANNEL_ID)
        chat_ch = guild.get_channel(CHAT_CHANNEL_ID)
        
        print(f"  📢 Channel 'ruang-interogasi': {'✅ Ditemukan' if intro_ch else '❌ Tidak ditemukan'}")
        print(f"  📢 Channel 'ganti-username': {'✅ Ditemukan' if change_ch else '❌ Tidak ditemukan'}")
        print(f"  📢 Channel 'obrolan-santai': {'✅ Ditemukan' if chat_ch else '❌ Tidak ditemukan'}")
    
    print("\n🚀 Bot siap menerima perintah!")
    print("=" * 50)

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ ERROR di event {event}:")
    traceback.print_exc()

@bot.event
async def on_member_join(member):
    try:
        print(f"👋 Member baru join: {member} ({member.id})")
        guild = member.guild
        unverified_role = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE_NAME)
        
        if unverified_role:
            await member.add_roles(unverified_role)
            print(f"  ✅ Role Unverified ditambahkan ke {member}")
            
            intro_channel = bot.get_channel(INTRO_CHANNEL_ID)
            if intro_channel:
                await intro_channel.send(
                    f"Hai {member.mention}! 🎮\n"
                    f"Silakan masukkan **username Roblox** kamu di sini.\n"
                    f"Contoh: ketik `rinanti`"
                )
                print(f"  ✅ Welcome message dikirim ke {intro_channel.name}")
        else:
            print(f"  ⚠️ Role 'Unverified' tidak ditemukan!")
            
    except Exception as e:
        print(f"❌ ERROR di on_member_join: {e}")
        traceback.print_exc()

@bot.event
async def on_message(message):
    try:
        if message.author.bot:
            return
        
        # Log setiap pesan di channel yang dimonitor
        if message.channel.id in [INTRO_CHANNEL_ID, CHANGE_NAME_CHANNEL_ID]:
            channel_name = message.channel.name if hasattr(message.channel, 'name') else 'Unknown'
            print(f"\n📨 Pesan diterima:")
            print(f"   Channel: #{channel_name} (ID: {message.channel.id})")
            print(f"   Author: {message.author} (ID: {message.author.id})")
            print(f"   Content: {message.content}")
        
        guild = message.guild
        member = message.author
        
        # Verifikasi otomatis (user baru)
        if message.channel.id == INTRO_CHANNEL_ID:
            print("   → Menjalankan handle_verification (user baru)")
            await handle_verification(message, guild, member, is_new_user=True)
        
        # Ganti username manual (user lama/semua user)
        elif message.channel.id == CHANGE_NAME_CHANNEL_ID:
            print("   → Menjalankan handle_verification (ganti username)")
            await handle_verification(message, guild, member, is_new_user=False)
        
        await bot.process_commands(message)
        
    except Exception as e:
        print(f"❌ ERROR di on_message: {e}")
        traceback.print_exc()

async def handle_verification(message, guild, member, is_new_user):
    try:
        roblox_name = message.content.strip()
        
        print(f"   🔍 Memproses: '{roblox_name}'")
        
        # Validasi input
        if len(roblox_name) < 3 or " " in roblox_name or not roblox_name.replace("_", "").isalnum():
            print(f"   ❌ Format tidak valid")
            await message.channel.send(
                f"❌ {member.mention} Format tidak valid! Gunakan huruf, angka, atau underscore.\n"
                f"Contoh: `olive` atau `player_123`"
            )
            return
        
        # Ambil nama asli Discord user
        discord_name = member.name
        new_nick = f"{discord_name} - {roblox_name}"
        
        print(f"   🔄 Mencoba ganti nickname menjadi: {new_nick}")
        
        # Cek role hierarchy
        bot_member = guild.get_member(bot.user.id)
        if bot_member.top_role <= member.top_role and guild.owner_id != bot.user.id:
            print(f"   ❌ Role hierarchy error - Bot role: {bot_member.top_role.position}, Member role: {member.top_role.position}")
            await message.channel.send(
                f"❌ {member.mention} Bot tidak bisa ganti nickname kamu karena role kamu lebih tinggi dari bot!\n"
                f"Hubungi admin untuk memindahkan role bot lebih tinggi."
            )
            return
        
        # Ganti nickname
        await member.edit(nick=new_nick)
        print(f"   ✅ Nickname berhasil diganti!")
        
        # Kelola role
        verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
        unverified_role = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE_NAME)
        
        if unverified_role and unverified_role in member.roles:
            await member.remove_roles(unverified_role)
            print(f"   ✅ Role Unverified dihapus")
        
        if verified_role and verified_role not in member.roles:
            await member.add_roles(verified_role)
            print(f"   ✅ Role Member ditambahkan")
        
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
        
        print(f"   ✅ Proses selesai untuk {member}")
        
    except discord.Forbidden as e:
        print(f"   ❌ Permission error: {e}")
        await message.channel.send(
            f"❌ {member.mention} Bot tidak punya izin untuk mengubah nickname atau role!\n"
            f"Hubungi admin untuk memberikan permission `Manage Nicknames` dan `Manage Roles` ke bot."
        )
        
    except discord.HTTPException as e:
        print(f"   ❌ HTTP error: {e}")
        await message.channel.send(
            f"⚠️ {member.mention} Terjadi kesalahan saat mengubah nickname. Error: {str(e)}"
        )
        
    except Exception as e:
        print(f"   ❌ Unexpected error: {type(e).__name__}: {e}")
        traceback.print_exc()
        await message.channel.send(
            f"⚠️ {member.mention} Terjadi kesalahan. Hubungi admin."
        )

# Jalankan bot dengan error handling
if __name__ == "__main__":
    try:
        print("🚀 Memulai bot...")
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ FATAL ERROR saat menjalankan bot: {e}")
        traceback.print_exc()
        sys.exit(1)
