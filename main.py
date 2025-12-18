import os
import sys
import discord
from discord.ext import commands
import traceback
import re

# === CONFIGURASI UTAMA ===
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

# Channel IDs (Verifikasi Roblox)
INTRO_CHANNEL_ID = 1448237276642410589      # 📰︱ruang-interogasi
CHANGE_NAME_CHANNEL_ID = 1448292386932527156  # 👨︱ganti-username
CHAT_CHANNEL_ID = 1447842346183168062        # 💬︱obrolan-santai

# Role Names (Verifikasi)
UNVERIFIED_ROLE_NAME = "Unverified"
VERIFIED_ROLE_NAME = "Member"

# === VIP CONFIG (SEMUA PAKAI ROLE ID) ===
VIP_LOUNGE_ROLE_ID = 1449683669471199243  # VIP LOUNGE
VIP1_ROLE_ID = 1448579620311142423        # VIP 1
VIP2_ROLE_ID = 1448580057181196440        # VIP 2
ADMIN_ROLE_NAME = "SUPER-ADMIN"

VIP1_CHANNEL_ID = 1447843476111626250    # 👑︱vip-1
VIP2_CHANNEL_ID = 1447845723239612457    # 🍹︱vip-2

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

# === HELPER FUNCTIONS ===
def has_admin_role(member):
    return any(role.name == ADMIN_ROLE_NAME for role in member.roles)

# === EVENTS ===
@bot.event
async def on_ready():
    print("=" * 50)
    print(f"✅ Bot {bot.user} berhasil online!")
    print(f"📡 Bot ID: {bot.user.id}")
    print(f"📡 Terhubung ke {len(bot.guilds)} server")
    print("=" * 50)

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

        intro_ch = guild.get_channel(INTRO_CHANNEL_ID)
        change_ch = guild.get_channel(CHANGE_NAME_CHANNEL_ID)
        chat_ch = guild.get_channel(CHAT_CHANNEL_ID)
        vip1_ch = guild.get_channel(VIP1_CHANNEL_ID)
        vip2_ch = guild.get_channel(VIP2_CHANNEL_ID)

        print(f"  📢 'ruang-interogasi': {'✅' if intro_ch else '❌'}")
        print(f"  📢 'ganti-username': {'✅' if change_ch else '❌'}")
        print(f"  📢 'obrolan-santai': {'✅' if chat_ch else '❌'}")
        print(f"  📢 '👑︱vip-1': {'✅' if vip1_ch else '❌'}")
        print(f"  📢 '🍹︱vip-2': {'✅' if vip2_ch else '❌'}")

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

async def handle_verification(message, guild, member, is_new_user):
    try:
        roblox_name = message.content.strip()

        if len(roblox_name) < 3 or " " in roblox_name or not roblox_name.replace("_", "").isalnum():
            await message.channel.send(
                f"❌ {member.mention} Format tidak valid! Gunakan huruf, angka, atau underscore.\n"
                f"Contoh: `olive` atau `player_123`"
            )
            return

        discord_name = member.name
        new_nick = f"{discord_name} - {roblox_name}"

        bot_member = guild.get_member(bot.user.id)
        if bot_member.top_role <= member.top_role and guild.owner_id != bot.user.id:
            await message.channel.send(
                f"❌ {member.mention} Bot tidak bisa ganti nickname kamu karena role kamu lebih tinggi dari bot!\n"
                f"Hubungi admin untuk memindahkan role bot lebih tinggi."
            )
            return

        await member.edit(nick=new_nick)

        verified_role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
        unverified_role = discord.utils.get(guild.roles, name=UNVERIFIED_ROLE_NAME)

        if unverified_role and unverified_role in member.roles:
            await member.remove_roles(unverified_role)

        if verified_role and verified_role not in member.roles:
            await member.add_roles(verified_role)

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
        await message.channel.send(
            f"❌ {member.mention} Bot tidak punya izin untuk mengubah nickname atau role!\n"
            f"Hubungi admin untuk memberikan permission `Manage Nicknames` dan `Manage Roles`."
        )
    except discord.HTTPException as e:
        await message.channel.send(f"⚠️ {member.mention} Error: {str(e)}")
    except Exception as e:
        print(f"   ❌ Unexpected error: {type(e).__name__}: {e}")
        traceback.print_exc()
        await message.channel.send(f"⚠️ {member.mention} Terjadi kesalahan. Hubungi admin.")

# === ON MESSAGE (GABUNGAN SEMUA LOGIKA) ===
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # --- HANDLE SEMUA COMMAND !! (HANYA UNTUK SUPER-ADMIN) ---
    if message.content.startswith("!!") and has_admin_role(message.author):
        content = message.content.strip()
        guild = message.guild

        # !!pull1 → hapus VIP LOUNGE dari semua, beri VIP 1
        if content == "!!pull1":
            vip_lounge_role = guild.get_role(VIP_LOUNGE_ROLE_ID)
            vip1_role = guild.get_role(VIP1_ROLE_ID)

            if not vip_lounge_role:
                await message.channel.send(f"❌ Role VIP LOUNGE (ID: {VIP_LOUNGE_ROLE_ID}) tidak ditemukan!")
                return
            if not vip1_role:
                await message.channel.send(f"❌ Role VIP 1 (ID: {VIP1_ROLE_ID}) tidak ditemukan!")
                return

            members_with_vip_lounge = [m for m in guild.members if vip_lounge_role in m.roles]
            if not members_with_vip_lounge:
                await message.channel.send("ℹ️ Tidak ada member yang memiliki role `VIP LOUNGE`.")
                return

            success_count = 0
            for member in members_with_vip_lounge:
                try:
                    await member.remove_roles(vip_lounge_role)
                    if vip1_role not in member.roles:
                        await member.add_roles(vip1_role)
                    success_count += 1
                except discord.Forbidden:
                    print(f"⚠️ Gagal ubah role untuk {member} (izin tidak cukup)")

            await message.channel.send(f"✅ Berhasil ubah `{success_count}` member dari `VIP LOUNGE` ke `VIP 1`.")

        # !!pull2 → hapus VIP LOUNGE dari semua, beri VIP 2
        elif content == "!!pull2":
            vip_lounge_role = guild.get_role(VIP_LOUNGE_ROLE_ID)
            vip2_role = guild.get_role(VIP2_ROLE_ID)

            if not vip_lounge_role:
                await message.channel.send(f"❌ Role VIP LOUNGE (ID: {VIP_LOUNGE_ROLE_ID}) tidak ditemukan!")
                return
            if not vip2_role:
                await message.channel.send(f"❌ Role VIP 2 (ID: {VIP2_ROLE_ID}) tidak ditemukan!")
                return

            members_with_vip_lounge = [m for m in guild.members if vip_lounge_role in m.roles]
            if not members_with_vip_lounge:
                await message.channel.send("ℹ️ Tidak ada member yang memiliki role `VIP LOUNGE`.")
                return

            success_count = 0
            for member in members_with_vip_lounge:
                try:
                    await member.remove_roles(vip_lounge_role)
                    if vip2_role not in member.roles:
                        await member.add_roles(vip2_role)
                    success_count += 1
                except discord.Forbidden:
                    print(f"⚠️ Gagal ubah role untuk {member} (izin tidak cukup)")

            await message.channel.send(f"✅ Berhasil ubah `{success_count}` member dari `VIP LOUNGE` ke `VIP 2`.")

        # !!v → beri VIP LOUNGE (untuk admin)
        elif content.startswith("!!v "):
            user_ids = []
            mentions = re.findall(r'<@!?(\d+)>', content)
            user_ids.extend([int(uid) for uid in mentions])
            if not user_ids:
                parts = content.split()
                for part in parts[1:]:
                    if part.isdigit() and len(part) >= 17:
                        user_ids.append(int(part))

            if not user_ids:
                await message.channel.send("❌ Tidak ada user yang valid. Gunakan: `!!v @user1 @user2` atau `!!v ID1 ID2`")
                return

            role = guild.get_role(VIP_LOUNGE_ROLE_ID)
            if not role:
                await message.channel.send(f"❌ Role VIP LOUNGE (ID: {VIP_LOUNGE_ROLE_ID}) tidak ditemukan!")
                return

            success_users = []
            already_have = []
            not_found = []

            for uid in user_ids:
                target = guild.get_member(uid)
                if not target:
                    not_found.append(str(uid))
                    continue

                if role in target.roles:
                    already_have.append(target.mention)
                else:
                    try:
                        await target.add_roles(role)
                        success_users.append(target.mention)
                    except discord.Forbidden:
                        print(f"⚠️ Gagal beri role ke {target} (izin tidak cukup)")

            msg_parts = []
            if success_users:
                msg_parts.append(f"✅ Berhasil beri role `VIP LOUNGE` ke: {', '.join(success_users)}")
            if already_have:
                msg_parts.append(f"ℹ️ Sudah punya role: {', '.join(already_have)}")
            if not_found:
                msg_parts.append(f"❌ User tidak ditemukan: {len(not_found)} ID")

            await message.channel.send("\n".join(msg_parts))

        # !!1 → beri VIP 1
        elif content.startswith("!!1 "):
            user_ids = []
            mentions = re.findall(r'<@!?(\d+)>', content)
            user_ids.extend([int(uid) for uid in mentions])
            if not user_ids:
                parts = content.split()
                for part in parts[1:]:
                    if part.isdigit() and len(part) >= 17:
                        user_ids.append(int(part))

            if not user_ids:
                await message.channel.send("❌ Tidak ada user yang valid. Gunakan: `!!1 @user1 @user2` atau `!!1 ID1 ID2`")
                return

            role = guild.get_role(VIP1_ROLE_ID)
            if not role:
                await message.channel.send(f"❌ Role VIP 1 (ID: {VIP1_ROLE_ID}) tidak ditemukan!")
                return

            success_users = []
            already_have = []
            not_found = []

            for uid in user_ids:
                target = guild.get_member(uid)
                if not target:
                    not_found.append(str(uid))
                    continue

                if role in target.roles:
                    already_have.append(target.mention)
                else:
                    try:
                        await target.add_roles(role)
                        success_users.append(target.mention)
                        vip1_channel = bot.get_channel(VIP1_CHANNEL_ID)
                        if vip1_channel:
                            await vip1_channel.send(f"{target.mention} telah diberikan akses ke channel VIP 1")
                    except discord.Forbidden:
                        print(f"⚠️ Gagal beri role ke {target} (izin tidak cukup)")

            msg_parts = []
            if success_users:
                msg_parts.append(f"✅ Berhasil beri `VIP 1` ke: {', '.join(success_users)}")
            if already_have:
                msg_parts.append(f"ℹ️ Sudah punya role: {', '.join(already_have)}")
            if not_found:
                msg_parts.append(f"❌ User tidak ditemukan: {len(not_found)} ID")

            await message.channel.send("\n".join(msg_parts))

        # !!2 → beri VIP 2
        elif content.startswith("!!2 "):
            user_ids = []
            mentions = re.findall(r'<@!?(\d+)>', content)
            user_ids.extend([int(uid) for uid in mentions])
            if not user_ids:
                parts = content.split()
                for part in parts[1:]:
                    if part.isdigit() and len(part) >= 17:
                        user_ids.append(int(part))

            if not user_ids:
                await message.channel.send("❌ Tidak ada user yang valid. Gunakan: `!!2 @user1 @user2` atau `!!2 ID1 ID2`")
                return

            role = guild.get_role(VIP2_ROLE_ID)
            if not role:
                await message.channel.send(f"❌ Role VIP 2 (ID: {VIP2_ROLE_ID}) tidak ditemukan!")
                return

            success_users = []
            already_have = []
            not_found = []

            for uid in user_ids:
                target = guild.get_member(uid)
                if not target:
                    not_found.append(str(uid))
                    continue

                if role in target.roles:
                    already_have.append(target.mention)
                else:
                    try:
                        await target.add_roles(role)
                        success_users.append(target.mention)
                        vip2_channel = bot.get_channel(VIP2_CHANNEL_ID)
                        if vip2_channel:
                            await vip2_channel.send(f"{target.mention} telah diberikan akses ke channel VIP 2")
                    except discord.Forbidden:
                        print(f"⚠️ Gagal beri role ke {target} (izin tidak cukup)")

            msg_parts = []
            if success_users:
                msg_parts.append(f"✅ Berhasil beri `VIP 2` ke: {', '.join(success_users)}")
            if already_have:
                msg_parts.append(f"ℹ️ Sudah punya role: {', '.join(already_have)}")
            if not_found:
                msg_parts.append(f"❌ User tidak ditemukan: {len(not_found)} ID")

            await message.channel.send("\n".join(msg_parts))

        # !!r → hapus role
        elif content.startswith("!!r "):
            arg = content[4:].strip()

            if arg.lower() == "vip1":
                role = guild.get_role(VIP1_ROLE_ID)
                if not role:
                    await message.channel.send(f"❌ Role VIP 1 tidak ditemukan!")
                    return
                members_to_remove = [m for m in guild.members if role in m.roles]
                if not members_to_remove:
                    await message.channel.send("ℹ️ Tidak ada user yang punya role `VIP 1`.")
                else:
                    for m in members_to_remove:
                        try:
                            await m.remove_roles(role)
                        except discord.Forbidden:
                            print(f"⚠️ Tidak bisa hapus role dari {m} (izin tidak cukup)")
                    await message.channel.send(f"✅ Berhasil hapus role `VIP 1` dari {len(members_to_remove)} user.")

            elif arg.lower() == "vip2":
                role = guild.get_role(VIP2_ROLE_ID)
                if not role:
                    await message.channel.send(f"❌ Role VIP 2 tidak ditemukan!")
                    return
                members_to_remove = [m for m in guild.members if role in m.roles]
                if not members_to_remove:
                    await message.channel.send("ℹ️ Tidak ada user yang punya role `VIP 2`.")
                else:
                    for m in members_to_remove:
                        try:
                            await m.remove_roles(role)
                        except discord.Forbidden:
                            print(f"⚠️ Tidak bisa hapus role dari {m} (izin tidak cukup)")
                    await message.channel.send(f"✅ Berhasil hapus role `VIP 2` dari {len(members_to_remove)} user.")

            elif arg.lower() == "viplounge":
                role = guild.get_role(VIP_LOUNGE_ROLE_ID)
                if not role:
                    await message.channel.send(f"❌ Role VIP LOUNGE tidak ditemukan!")
                    return
                members_to_remove = [m for m in guild.members if role in m.roles]
                if not members_to_remove:
                    await message.channel.send("ℹ️ Tidak ada user yang punya role `VIP LOUNGE`.")
                else:
                    for m in members_to_remove:
                        try:
                            await m.remove_roles(role)
                        except discord.Forbidden:
                            print(f"⚠️ Tidak bisa hapus role dari {m} (izin tidak cukup)")
                    await message.channel.send(f"✅ Berhasil hapus role `VIP LOUNGE` dari {len(members_to_remove)} user.")

            else:
                user_id = None
                mention_match = re.search(r'<@!?(\d+)>', arg)
                if mention_match:
                    user_id = int(mention_match.group(1))
                elif arg.isdigit() and len(arg) >= 17:
                    user_id = int(arg)

                if not user_id:
                    await message.channel.send("❌ Format salah. Gunakan: `!!r @user`, `!!r ID`, atau `!!r vip1` / `!!r vip2` / `!!r viplounge`")
                    return

                target = guild.get_member(user_id)
                if not target:
                    await message.channel.send("❌ User tidak ditemukan.")
                    return

                roles_removed = []
                vip1_role = guild.get_role(VIP1_ROLE_ID)
                vip2_role = guild.get_role(VIP2_ROLE_ID)
                vip_lounge_role = guild.get_role(VIP_LOUNGE_ROLE_ID)

                if vip1_role and vip1_role in target.roles:
                    await target.remove_roles(vip1_role)
                    roles_removed.append("VIP 1")
                if vip2_role and vip2_role in target.roles:
                    await target.remove_roles(vip2_role)
                    roles_removed.append("VIP 2")
                if vip_lounge_role and vip_lounge_role in target.roles:
                    await target.remove_roles(vip_lounge_role)
                    roles_removed.append("VIP LOUNGE")

                if roles_removed:
                    await message.channel.send(f"✅ Berhasil hapus role {', '.join(roles_removed)} dari {target.mention}")
                else:
                    await message.channel.send(f"ℹ️ {target.mention} tidak punya role VIP.")

        # Penting: JANGAN panggil bot.process_commands() → agar tidak muncul CommandNotFound
        # Hanya return setelah selesai
        return

    # --- HANDLE VERIFIKASI ROBLOX ---
    if message.channel.id in [INTRO_CHANNEL_ID, CHANGE_NAME_CHANNEL_ID]:
        guild = message.guild
        member = message.author

        if message.channel.id == INTRO_CHANNEL_ID:
            await handle_verification(message, guild, member, is_new_user=True)
        elif message.channel.id == CHANGE_NAME_CHANNEL_ID:
            await handle_verification(message, guild, member, is_new_user=False)

    # Jangan proses command lain (karena kita tidak pakai @bot.command)
    # Tapi biarkan message biasa tetap diproses (misal verifikasi)
    return

# === JALANKAN BOT ===
if __name__ == "__main__":
    try:
        print("🚀 Memulai bot...")
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ FATAL ERROR saat menjalankan bot: {e}")
        traceback.print_exc()
        sys.exit(1)
