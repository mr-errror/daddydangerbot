# bot.py
import discord
from discord import app_commands
from discord.ext import commands
import datetime
from typing import Optional
import os
import asyncio
import aiosqlite
import time
import datetime
import math
import random
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()
from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # required for moderation actions

DB_PATH = "bot_data.sqlite"
GUILD_ID = None  # Set to your guild ID for testing, or None for global
VERIFIED_ROLE_NAME = "Verified"
SPAM_WINDOW = 7        # seconds
SPAM_THRESHOLD = 5     # messages in SPAM_WINDOW triggers action
DUPLICATE_THRESHOLD = 4 # duplicates within small window
WARN_LIMIT = 3
MUTE_DURATION = 60 * 10  # 10 minutes default mute

bot = commands.Bot(command_prefix='/', intents=intents, help_command=None)

@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("hewo")

# Slash Command /about
@bot.tree.command(name="daddy-danger-abouts")
async def about(interaction: discord.Interaction):
    await interaction.response.send_message("I am a bot created by Error! yes the || alpha sigma male || made me 😎")

# Slash Command /randomnumber
@bot.tree.command(name="randomnumber")
async def randomnumber(interaction: discord.Interaction):
    import random
    num = random.randint(1, 100)
    await interaction.response.send_message(f"Your random number is: {num}")

# Slash Command /compliment
@bot.tree.command(name="compliment")
async def compliment(interaction: discord.Interaction):
    import random
    compliments = [
        "You’re awesome! 🌟",
        "Your smile lights up the room! 😊",
        "You’re a genius! 🧑‍💻",
        "**YOU** yes, **YOU** are an || alpha sigma male ||"
    ]
    await interaction.response.send_message(random.choice(compliments))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Reacting
    if "mr.error" in message.content.lower() or "error" in message.content.lower() or "eror" in message.content.lower():
        await message.channel.send("Oh **Error**?? The holy lord  **Error**... he is goated, no cap!!")
    
    if "ANGEL" in message.content.lower() or "angel" in message.content.lower():
        await message.channel.send("**angel** yeah that guy is goated fr fr, and why you mentioning him?")
    
    if "angle" in message.content.lower():
        await message.channel.send("YOU DUMBASS ITS PRONOUNCED AS **AN-GEL** YOU HEAR ME ?? YES SAY IT RESPECTFULLY !!")

    if "miki" in message.content.lower():
        await message.channel.send("AYE YOU!!! unpure soul dont you mention her she's sh- she is an angel 🙇‍♂🙇‍♂")

    # Don't forget to process slash commands!
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

    # Register commands once bot is ready
    await bot.tree.sync()  # This syncs the slash commands with Discord!

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user} (id: {bot.user.id})")
    # Sync slash commands to the guilds (global sync can take up to an hour;
    # for faster testing you can sync per-guild or run once)
    try:
        await bot.tree.sync()
        print("Slash commands synced.")
    except Exception as e:
        print("Failed to sync commands:", e)

# Utility checks
def has_guild_permissions(user: discord.Member, **perms):
    gp = user.guild_permissions
    return all(getattr(gp, name, False) == value for name, value in perms.items())

def check_hierarchy(interaction: discord.Interaction, target: discord.Member) -> Optional[str]:
    """Return error string if target cannot be moderated by the invoker/bot, else None."""
    invoker = interaction.user
    guild = interaction.guild
    bot_member = guild.me

    if target == invoker:
        return "You cannot perform this action on yourself."
    if target == bot_member:
        return "I can't perform that action on myself."
    # Invoker must have higher top role than target
    if isinstance(invoker, discord.Member) and target.top_role >= invoker.top_role and invoker != guild.owner:
        return "You can't moderate this user because their role is equal or higher than yours."
    # Bot must have higher top role than target
    if target.top_role >= bot_member.top_role and guild.owner_id != bot_member.id:
        return "I can't moderate this user because their role is equal or higher than mine."
    return None

# KICK
@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(member="Member to kick", reason="Reason for kick (optional)")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, kick_members=True):
        await interaction.response.send_message("You need the Kick Members permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, kick_members=True):
        await interaction.response.send_message("I don't have permission to kick members.", ephemeral=True); return

    bad = check_hierarchy(interaction, member)
    if bad:
        await interaction.response.send_message(bad, ephemeral=True); return

    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} has been kicked. Reason: {reason or 'No reason provided.'}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to kick: {e}", ephemeral=True)

# BAN
@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(member="Member to ban", reason="Reason for ban (optional)")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, ban_members=True):
        await interaction.response.send_message("You need the Ban Members permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, ban_members=True):
        await interaction.response.send_message("I don't have permission to ban members.", ephemeral=True); return

    bad = check_hierarchy(interaction, member)
    if bad:
        await interaction.response.send_message(bad, ephemeral=True); return

    try:
        await member.ban(reason=reason, delete_message_days=0)
        await interaction.response.send_message(f"✅ {member.mention} has been banned. Reason: {reason or 'No reason provided.'}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to ban: {e}", ephemeral=True)

# UNBAN (by user id)
@bot.tree.command(name="unban", description="Unban a user by ID")
@app_commands.describe(user_id="ID of the user to unban")
async def unban(interaction: discord.Interaction, user_id: int):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, ban_members=True):
        await interaction.response.send_message("You need the Ban Members permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, ban_members=True):
        await interaction.response.send_message("I don't have permission to unban members.", ephemeral=True); return

    try:
        user = await bot.fetch_user(user_id)
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"✅ Unbanned user {user} ({user.id}).")
    except Exception as e:
        await interaction.response.send_message(f"Failed to unban: {e}", ephemeral=True)

# TIMEOUT (moderate members)
@bot.tree.command(name="timeout", description="Timeout a member for X minutes")
@app_commands.describe(member="Member to timeout", minutes="Duration in minutes", reason="Reason (optional)")
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int = 10, reason: Optional[str] = None):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if minutes < 1 or minutes > 28*24*60:
        await interaction.response.send_message("Duration must be between 1 minute and 40320 minutes (28 days).", ephemeral=True); return
    if not has_guild_permissions(interaction.user, moderate_members=True):
        await interaction.response.send_message("You need the Moderate Members permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, moderate_members=True):
        await interaction.response.send_message("I don't have permission to timeout members.", ephemeral=True); return

    bad = check_hierarchy(interaction, member)
    if bad:
        await interaction.response.send_message(bad, ephemeral=True); return

    until = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)
    try:
        await member.edit(timeout=until, reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} timed out for {minutes} minute(s). Reason: {reason or 'No reason provided.'}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to timeout: {e}", ephemeral=True)

# UNTIMEOUT
@bot.tree.command(name="untimeout", description="Remove timeout from a member")
@app_commands.describe(member="Member to remove timeout from", reason="Reason (optional)")
async def untimeout(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, moderate_members=True):
        await interaction.response.send_message("You need the Moderate Members permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, moderate_members=True):
        await interaction.response.send_message("I don't have permission to modify timeouts.", ephemeral=True); return

    bad = check_hierarchy(interaction, member)
    if bad:
        await interaction.response.send_message(bad, ephemeral=True); return

    try:
        await member.edit(timeout=None, reason=reason)
        await interaction.response.send_message(f"✅ Removed timeout for {member.mention}.")
    except Exception as e:
        await interaction.response.send_message(f"Failed to remove timeout: {e}", ephemeral=True)

# PURGE (bulk delete)
@bot.tree.command(name="purge", description="Bulk delete messages from the channel (max 100)")
@app_commands.describe(number="Number of messages to delete (1-100)")
async def purge(interaction: discord.Interaction, number: int):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if number < 1 or number > 100:
        await interaction.response.send_message("You can delete between 1 and 100 messages.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, manage_messages=True):
        await interaction.response.send_message("You need Manage Messages permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, manage_messages=True):
        await interaction.response.send_message("I don't have Manage Messages permission.", ephemeral=True); return

    # Acknowledge the command first (to avoid "This interaction failed" if purge takes time)
    await interaction.response.defer(ephemeral=True)
    try:
        deleted = await interaction.channel.purge(limit=number)
        await interaction.followup.send(f"✅ Deleted {len(deleted)} messages.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Failed to purge: {e}", ephemeral=True)

# LOCK / UNLOCK channel
@bot.tree.command(name="lock", description="Lock this channel (deny @everyone send messages)")
async def lock(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, manage_channels=True):
        await interaction.response.send_message("You need Manage Channels permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, manage_channels=True):
        await interaction.response.send_message("I don't have Manage Channels permission.", ephemeral=True); return

    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 Channel locked. @everyone cannot send messages.")
    except Exception as e:
        await interaction.response.send_message(f"Failed to lock channel: {e}", ephemeral=True)

@bot.tree.command(name="unlock", description="Unlock this channel")
async def unlock(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, manage_channels=True):
        await interaction.response.send_message("You need Manage Channels permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, manage_channels=True):
        await interaction.response.send_message("I don't have Manage Channels permission.", ephemeral=True); return

    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=None)
        await interaction.response.send_message("🔓 Channel unlocked.")
    except Exception as e:
        await interaction.response.send_message(f"Failed to unlock channel: {e}", ephemeral=True)

# WARN (DM the user)
@bot.tree.command(name="warn", description="Send a warning DM to a member")
@app_commands.describe(member="Member to warn", reason="Reason for the warning (optional)")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, kick_members=True):
        await interaction.response.send_message("You need moderator permissions (Kick/Ban) to warn members.", ephemeral=True); return

    bad = check_hierarchy(interaction, member)
    if bad:
        await interaction.response.send_message(bad, ephemeral=True); return

    try:
        await member.send(f"You have been warned in **{interaction.guild.name}** by **{interaction.user}**.\nReason: {reason or 'No reason provided.'}")
        await interaction.response.send_message(f"✅ {member.mention} has been warned (DM sent).")
    except Exception as e:
        await interaction.response.send_message(f"Failed to DM the user: {e}", ephemeral=True)

# Generic error handler for app commands
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    # You can expand specific error types here
    await interaction.response.send_message(f"Error: {error}", ephemeral=True)

# -------- Helpers --------
def snowflake_to_datetime(snowflake: int) -> datetime.datetime:
    """
    Convert a Discord snowflake to creation datetime (UTC).
    Formula: (snowflake >> 22) + discord_epoch
    """
    DISCORD_EPOCH = 1420070400000  # milliseconds
    ts = ((snowflake >> 22) + DISCORD_EPOCH) / 1000
    return datetime.datetime.utcfromtimestamp(ts)

def pretty_timedelta(dt: datetime.datetime) -> str:
    now = datetime.datetime.utcnow()
    diff = now - dt
    days = diff.days
    hours, rem = divmod(diff.seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{days}d {hours}h {minutes}m"

# -------- Storage Models --------
@dataclass
class WarningRecord:
    user_id: int
    guild_id: int
    moderator_id: int
    reason: str
    timestamp: float

# -------- In-memory anti-spam state --------
user_message_times = defaultdict(lambda: deque(maxlen=64))
user_recent_content = defaultdict(lambda: deque(maxlen=32))

# -------- DB Setup --------
async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                guild_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                ts REAL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS mutes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                guild_id INTEGER,
                unmute_ts REAL
            )
        """)
        await db.commit()

# -------- Bot Events --------
@bot.event
async def on_ready():
    await init_db()
    print(f"Logged in as {bot.user} (id: {bot.user.id})")
    print("------")
    check_unmutes.start()

@bot.event
async def on_guild_join(guild):
    # Create Verified role if not present (optional)
    existing = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
    if existing is None:
        try:
            await guild.create_role(name=VERIFIED_ROLE_NAME, reason="Auto-created Verified role for verification flow")
            print(f"Created role {VERIFIED_ROLE_NAME} in {guild.name}")
        except Exception as e:
            print("Could not create Verified role:", e)

@bot.event
async def on_message(message: discord.Message):
    # Bail for bot messages
    if message.author.bot:
        return

    # Optional: limit to one guild if configured
    if GUILD_ID and getattr(message.guild, "id", None) != GUILD_ID:
        return

    # Track message timestamps for spam detection
    now = time.time()
    q = user_message_times[message.author.id]
    q.append(now)

    # Track message content for duplicate detection (simple)
    content_q = user_recent_content[message.author.id]
    content_q.append(message.content.strip().lower())

    # Spam heuristic: N messages in M seconds
    if len(q) >= SPAM_THRESHOLD and (q[-1] - q[-SPAM_THRESHOLD] <= SPAM_WINDOW):
        # found spammy burst
        try:
            await take_action_on_spam(message)
        except Exception as e:
            print("Error handling spam:", e)

    # Duplicate message heuristic
    if len(content_q) >= DUPLICATE_THRESHOLD:
        last = content_q[-1]
        dup_count = sum(1 for c in content_q if c and c == last)
        if dup_count >= DUPLICATE_THRESHOLD:
            try:
                await take_action_on_spam(message, reason="Duplicate-messages")
            except Exception as e:
                print("Error handling duplicate spam:", e)

    await bot.process_commands(message)

# -------- Spam handling & actions --------
async def take_action_on_spam(message: discord.Message, reason: str = "Spam detected"):
    guild = message.guild
    member = message.author
    # Delete the recent messages from member (best-effort)
    if guild and guild.me.guild_permissions.manage_messages:
        def is_by_author(m):
            return m.author.id == member.id
        try:
            deleted = await message.channel.purge(limit=50, check=is_by_author)
            print(f"Purged {len(deleted)} messages from {member} in {guild.name}")
        except Exception as e:
            print("Purge failed:", e)

    # Warn and mute if repeated
    await add_warning(member.id, guild.id if guild else 0, bot.user.id, reason)
    warns = await count_warnings(member.id, guild.id if guild else 0)
    if warns >= WARN_LIMIT:
        await apply_temporary_mute(member, guild, duration=MUTE_DURATION, reason=f"Auto-mute after {warns} warns for spam")

async def add_warning(user_id: int, guild_id: int, moderator_id: int, reason: str):
    ts = time.time()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO warnings (user_id, guild_id, moderator_id, reason, ts) VALUES (?, ?, ?, ?, ?)",
                         (user_id, guild_id, moderator_id, reason, ts))
        await db.commit()

async def count_warnings(user_id: int, guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM warnings WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
        row = await cur.fetchone()
        return row[0] if row else 0

async def apply_temporary_mute(member: discord.Member, guild: discord.Guild, duration: int = MUTE_DURATION, reason: str = "Temporary mute"):
    # Try to add "Muted" role; if not present, create it
    role = discord.utils.get(guild.roles, name="Muted")
    if role is None:
        perms = discord.Permissions(send_messages=False, add_reactions=False)
        try:
            role = await guild.create_role(name="Muted", reason="Auto-created muted role")
            # Try set for every text channel (best effort)
            for ch in guild.text_channels:
                try:
                    await ch.set_permissions(role, send_messages=False, add_reactions=False)
                except Exception:
                    pass
        except Exception as e:
            print("Failed creating Muted role:", e)
            return
    try:
        await member.add_roles(role, reason=reason)
    except Exception as e:
        print("Failed to add muted role:", e)
        return

    unmute_ts = time.time() + duration
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("INSERT INTO mutes (user_id, guild_id, unmute_ts) VALUES (?, ?, ?)",
                         (member.id, guild.id, unmute_ts))
        await db.commit()
    try:
        await member.send(f"You were muted in {guild.name} for: {reason}. Duration: {duration} seconds.")
    except Exception:
        pass

@tasks.loop(seconds=30)
async def check_unmutes():
    now = time.time()
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT id, user_id, guild_id, unmute_ts FROM mutes WHERE unmute_ts <= ?", (now,))
        rows = await cur.fetchall()
        for row in rows:
            _id, user_id, guild_id, unmute_ts = row
            guild = bot.get_guild(guild_id)
            if guild:
                member = guild.get_member(user_id)
                muted_role = discord.utils.get(guild.roles, name="Muted")
                if member and muted_role:
                    try:
                        await member.remove_roles(muted_role, reason="Auto unmute")
                    except Exception:
                        pass
            await db.execute("DELETE FROM mutes WHERE id = ?", (_id,))
        await db.commit()

# -------- Commands: Info & moderation --------
@bot.command(name="userinfo")
@commands.has_permissions(kick_members=True)
async def userinfo(ctx, member: discord.Member):
    """
    Show core info about a user (account creation, join date, warns).
    Note: cannot access platform-wide message history. Only data accessible via bot/guild.
    """
    created = snowflake_to_datetime(member.id)
    joined = getattr(member, "joined_at", None)
    warns = await count_warnings(member.id, ctx.guild.id if ctx.guild else 0)
    embed = discord.Embed(title=f"User info — {member}", color=discord.Color.blurple())
    embed.set_thumbnail(url=member.display_avatar.url if member.display_avatar else discord.Embed.Empty)
    embed.add_field(name="ID", value=str(member.id), inline=False)
    embed.add_field(name="Account created (UTC)", value=f"{created.isoformat()} ({pretty_timedelta(created)} ago)", inline=False)
    embed.add_field(name="Joined server", value=str(joined) if joined else "N/A", inline=False)
    embed.add_field(name="Warnings (this server)", value=str(warns), inline=False)
    # Attempt to fetch audit log entries related to user (requires view_audit_log)
    if ctx.guild and ctx.guild.me.guild_permissions.view_audit_log:
        try:
            entries = []
            async for e in ctx.guild.audit_logs(limit=5, user=member):
                entries.append(f"{e.action.name} by {e.user} at {e.created_at.isoformat()}")
            if entries:
                embed.add_field(name="Recent audit log hits", value="\n".join(entries[:5]), inline=False)
        except Exception:
            pass
    await ctx.send(embed=embed)

@bot.command(name="warn")
@commands.has_permissions(kick_members=True)
async def warn(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    await add_warning(member.id, ctx.guild.id if ctx.guild else 0, ctx.author.id, reason)
    warns = await count_warnings(member.id, ctx.guild.id if ctx.guild else 0)
    await ctx.send(f"{member.mention} has been warned. Total warns: {warns}. Reason: {reason}")
    try:
        await member.send(f"You were warned in {ctx.guild.name}: {reason}. Total warns: {warns}")
    except Exception:
        pass

@bot.command(name="warnings")
@commands.has_permissions(kick_members=True)
async def warnings_cmd(ctx, member: discord.Member = None):
    member = member or ctx.author
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT moderator_id, reason, ts FROM warnings WHERE user_id = ? AND guild_id = ? ORDER BY ts DESC LIMIT 50",
                               (member.id, ctx.guild.id if ctx.guild else 0))
        rows = await cur.fetchall()
        if not rows:
            await ctx.send("No warnings found.")
            return
        txt = []
        for mod_id, reason, ts in rows:
            t = datetime.datetime.utcfromtimestamp(ts).isoformat()
            txt.append(f"[{t}] by <@{mod_id}>: {reason}")
        await ctx.send(f"Warnings for {member}:\n" + "\n".join(txt[:20]))

@bot.command(name="mute")
@commands.has_permissions(moderate_members=True)
async def mute_cmd(ctx, member: discord.Member, minutes: int = 10, *, reason: str = "No reason"):
    await apply_temporary_mute(member, ctx.guild, duration=minutes*60, reason=reason)
    await ctx.send(f"{member.mention} muted for {minutes} minute(s). Reason: {reason}")

@bot.command(name="audit")
@commands.has_permissions(view_audit_log=True)
async def audit_cmd(ctx, limit: int = 5):
    if not ctx.guild.me.guild_permissions.view_audit_log:
        await ctx.send("I do not have permission to view audit logs.")
        return
    lines = []
    async for entry in ctx.guild.audit_logs(limit=limit):
        t = entry.created_at.isoformat()
        lines.append(f"{t} — {entry.action.name} — target: {entry.target} — by: {entry.user}")
    await ctx.send("Recent audit log entries:\n" + "\n".join(lines) if lines else "No audit log entries available.")

# -------- Verification flow --------
@bot.command(name="verify")
async def verify_cmd(ctx):
    """
    Simple verification flow:
    - Creates 'Verified' role (if missing)
    - Asks a tiny DM captcha (math) — user must reply correctly within time
    """
    member = ctx.author
    guild = ctx.guild
    if not guild:
        await ctx.send("Verification works in servers only.")
        return

    role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
    if role is None:
        try:
            role = await guild.create_role(name=VERIFIED_ROLE_NAME, reason="Auto-created Verified role")
        except Exception as e:
            await ctx.send("Couldn't create Verified role; ask an admin to create it for me.")
            return

    # Send DM with a simple math captcha
    import random
    a, b = random.randint(2, 15), random.randint(2, 15)
    answer = a + b
    try:
        dm = await member.send(f"Please solve to verify in **{guild.name}**: what is {a} + {b}? You have 90s.")
    except Exception:
        await ctx.send("I couldn't DM you. Please enable DMs or contact a moderator.")
        return

    def check(m):
        return m.author.id == member.id and isinstance(m.channel, discord.DMChannel)

    try:
        resp = await bot.wait_for("message", check=check, timeout=90)
        if resp.content.strip() == str(answer):
            try:
                await member.add_roles(role, reason="Passed verification captcha")
                await member.send(f"Verified in {guild.name}. Role assigned.")
                await ctx.send(f"{member.mention}, verified successfully.")
            except Exception:
                await member.send("I couldn't assign the role. Ask an admin to check my permissions.")
                await ctx.send("I couldn't assign the role. Ask an admin to check my permissions.")
        else:
            await member.send("Wrong answer. Verification failed.")
            await ctx.send(f"{member.mention} failed verification.")
    except asyncio.TimeoutError:
        await member.send("Timed out. Try `!verify` again.")
        await ctx.send(f"{member.mention}, verification timed out.")

# -------- Utility commands --------
@bot.command(name="help")
async def help_cmd(ctx):
    txt = (
        "**Moderation & Verification Bot**\n"
        "Commands:\n"
        "`!verify` - DM math captcha and assign Verified role\n"
        "`!userinfo @user` - show account creation, join date, warns (mod only)\n"
        "`!warn @user <reason>` - add a warning (mod only)\n"
        "`!warnings [@user]` - list warnings\n"
        "`!mute @user [minutes]` - mute with Muted role (mod only)\n"
        "`!audit [limit]` - show recent audit log entries (requires permission)\n"
    )
    await ctx.send(txt)

# -------- Limitations & safety: explain when asked --------
@bot.command(name="limits")
async def limits(ctx):
    txt = (
        "What I cannot do:\n"
        "- I cannot read DMs of other users.\n"
        "- I cannot access message history outside servers where I'm a member.\n"
        "- I cannot perform any action that violates Discord TOS (no account hijacking, scraping beyond API limits, etc.).\n\n"
        "What I can do: audit logs (if permitted), detect spam heuristically, mute/kick/ban, assign roles, and store warnings."
    )
    await ctx.send(txt)


# Run the bot
import os
TOKEN = os.getenv("BOT_TOKEN")

