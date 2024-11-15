import json
from asyncio import Lock
import asyncio
import utils
import discord
from discord.ext import commands
import settings

intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=settings.BOT_PREFIX,
    description=settings.BOT_DESCRIPTION,
    intents=intents,
)
bot.linked_wallets = {}


@bot.event
async def on_ready():
    for cog in [
        "cogs.drop",
        "cogs.collectionbook",
        "cogs.chatloot",
        "cogs.util",
#        "cogs.trickortreat",
    ]:
        await bot.load_extension(cog)
    print(f"We have logged in as {bot.user}")


@bot.command()
@commands.is_owner()
async def load(ctx, cog: str):
    try:
        await bot.load_extension(cog)
    except Exception as e:
        await ctx.send(e)
    else:
        await ctx.send("Cog " + "'" + cog + "'" + " has been loaded.")


@bot.command()
@commands.is_owner()
async def unload(ctx, cog: str):
    try:
        await bot.unload_extension(cog)
    except Exception as e:
        await ctx.send(e)
    else:
        await ctx.send("Cog " + "'" + cog + "'" + " has been unloaded.")


@bot.command()
@commands.is_owner()
async def reload(ctx, cog: str):
    try:
        await bot.unload_extension(cog)
        await bot.load_extension(cog)
    except Exception as e:
        await ctx.send(e)
    else:
        await ctx.send("Cog " + "'" + cog + "'" + " has been reloaded.")


bot.run(settings.DISCORD_BOT_TOKEN)
