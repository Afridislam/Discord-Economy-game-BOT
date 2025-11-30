
import discord
from discord.ext import commands
import aiosqlite

async def get_prefix(bot, message):
    if message.guild:
        async with aiosqlite.connect("data/prefixes.db") as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS prefixes (
                    guild_id INTEGER PRIMARY KEY,
                    prefix TEXT
                )
            """)
            async with db.execute("SELECT prefix FROM prefixes WHERE guild_id = ?", (message.guild.id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]
    return "!"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=get_prefix, intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

initial_extensions = [
    "cogs.economy",
    "cogs.daily",
    "cogs.gamble",
    "cogs.help_cog",
    "cogs.profile"
]

async def setup():
    for ext in initial_extensions:
        await bot.load_extension(ext)

import asyncio
asyncio.run(setup())

@bot.command(name="setprefix")
@commands.has_permissions(administrator=True)
async def set_prefix(ctx, prefix: str):
    async with aiosqlite.connect("data/prefixes.db") as db:
        await db.execute("INSERT OR REPLACE INTO prefixes (guild_id, prefix) VALUES (?, ?)", (ctx.guild.id, prefix))
        await db.commit()
    await ctx.send(f"✅ Prefix changed to: `{prefix}`")

@set_prefix.error
async def set_prefix_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You need Administrator permission to use this command.")
    else:
        await ctx.send(f"❌ Error: {error}")

bot.run("YOUR_BOT_TOKEN")
