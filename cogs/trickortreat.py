from discord.ext import commands
import settings
import secrets
import discord
import settings
from datetime import date
import datetime
import utils 
from aioeosabi import EosAccount


class TrickOrTreat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot          
        self.used_treat = {}
        self.last_timeouts = {}
        print("Trick o Treat cog loaded")


    @commands.command(description="Test your luck, you may just win a NFT.",
                      aliases=["santa"])
    @commands.check(lambda ctx: ctx.guild and ctx.guild.id == settings.GUILD)  # 
    @commands.has_any_role(1140028262207201280) #Verified role
    async def trickortreat(self, ctx):
        if ctx.channel.id != 1290748756127645767:
            return
        special_wallet = EosAccount("waifustreats", private_key= settings.WAX_ACC_PRIVKEY)

        userid = ctx.author.id
        if userid in self.used_treat and self.used_treat[userid] == date.today().strftime("%d-%m"):
            await ctx.message.add_reaction("🕐")  
            await ctx.channel.send("You've already tried your luck today! Come back tomorrow")
            return
        self.used_treat[userid] = date.today().strftime("%d-%m")
        await ctx.message.add_reaction("🏡") 

        randomness = secrets.randbelow(100)
        
        if 1138220294713126993 in [role.id for role in ctx.author.roles] and randomness < 10:
            await ctx.channel.send("Bonus Prize! Enjoy a pink fairy NFT drop")

            log_additional = f" Lucky trick or treat bonus drop!"
            try:
                await utils.drop_random_from_wallet(bot = self.bot, drop_message = ctx.message, member = ctx.author, memo =  "Bonus Treat! You've won a random Waifu NFT", log_additional =  log_additional, emoji_sequences = ["<:businessbebe:1139294276065439745>","<:waifustonks:1212006102787555430>"])
            except Exception as e:
                print("Ran into an error. Please ping Majic!")
                print(e)

        elif randomness < 25:
            timeout_duration = secrets.randbelow(300) + 15 
            timeout = 0
            if userid in self.last_timeouts: 
                timeout = self.last_timeouts[userid] ** 2 // 60
            await ctx.message.add_reaction("🥚")
            await ctx.channel.send("Trick! You didn't get lucky today!")
            await ctx.author.timeout(discord.utils.utcnow() + datetime.timedelta(seconds = timeout_duration + timeout), reason="Trick! You didn't get lucky today")
            self.last_timeouts[userid] = timeout_duration
            return 
        try:
            self.last_timeouts[userid] = 0

            
            log_additional = f" Trick or Treat drop from daily command."
            await utils.drop_random_from_wallet(bot = self.bot, drop_message = ctx.message, member = ctx.author, memo =  "Bonus Treat! You've won a random Waifu NFT", log_additional =  log_additional, emoji_sequences = ["👻", "🍬"], account = special_wallet)

        except Exception as e:
            await ctx.send(f"Ran into an error. Please ping Majic!: {e}\n")


async def setup(bot):
	await bot.add_cog(TrickOrTreat(bot))

