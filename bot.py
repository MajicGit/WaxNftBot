import json
from asyncio import Lock
import asyncio
import utils
import discord
from discord.ext import commands
import settings
# Mutex for when we open the file

intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True 
intents.message_content = True

bot = commands.Bot(command_prefix='-', description='Wax Waifus NFT Tipbot', intents = intents)



@bot.event
async def on_ready():
	for cog in ['cogs.drop']:
		await bot.load_extension(cog)
	print(f'We have logged in as {bot.user}')


@bot.command(name='hi')
async def hi(ctx):
	print("Hi command")
	await ctx.send("Hello there")

@bot.command() #The next three commands allow you to load/unload cogs on the fly. You must set up bot.owner_id for these to work.
@commands.is_owner()
async def load(ctx, cog:str):
	try:
		bot.load_extension(cog)
	except Exception as e:
		await ctx.send(e)
	else:
		await ctx.send('Cog ' + "'" + cog + "'" + ' has been loaded.')
		
@bot.command()
@commands.is_owner()
async def unload(ctx, cog:str):
	try:
		bot.unload_extension(cog)
	except Exception as e:
		await ctx.send(e)
	else:
		await ctx.send('Cog ' + "'" + cog + "'" + ' has been unloaded.')
		
@bot.command()
@commands.is_owner()
async def reload(ctx, cog:str):
	try:
		bot.unload_extension(cog)
		bot.load_extension(cog)
	except Exception as e:
		await ctx.send(e)
	else:
		await ctx.send('Cog ' + "'" + cog + "'" + ' has been reloaded.')

	
bot.run(settings.DISCORD_BOT_TOKEN) 
