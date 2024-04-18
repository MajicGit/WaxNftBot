import discord
from discord.ext import commands
from typing import Union
import utils 
import settings
import secrets
class Drop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  
        print("Drop cog loaded")
		
    @commands.command(description="Send the specified discord user a claim link with a random NFT per DM.",
                      aliases=["loot","reward"])
    @commands.has_any_role(1138222735827423252, 1137852719328137317, 1019942433485754488)
    async def drop(self, ctx, member: discord.Member, *, memo: str = "Congratulations you've won a random Waifu NFT!"):
        try:
            await ctx.message.add_reaction("📬")
            available_assets = (await utils.try_api_request(f"/atomicassets/v1/assets?owner={settings.WAX_ACC_NAME}&page=1&limit=1000",endpoints=utils.aa_api_list))['data']
            if len(available_assets) == 0:
                await ctx.send(f"Error sending claimlink: No thewaxwaifu assets in wallet {settings.WAX_ACC_NAME} found")
                return
            to_send = secrets.choice(available_assets)['asset_id']
            
            claimlink = await utils.gen_claimlink([to_send], memo = memo + " Remember to claim this link, otherwise all unclaimed links will be reclaimed by The Pink Fairy after 31 days!") 
            print(claimlink)

            if "https://wax.atomichub.io/trading/link/" not in claimlink:
                await ctx.send(f"Link generation failed! {claimlink}. Please try again and/or ping Majic")


            user_message = f"""Congratulations, the Pink Fairy sent you a random NFT!\nYou can claim it by clicking the following link (just login with your wax_chain wallet, might require allowing popups): {claimlink}\n**WARNING: Anyone you share this link with can claim it, so, do not share with anyone if you do not want to give the NFT away!**\n__Also, please, avoid scams:__\n- Before clicking a claim link, ensure the top level domain is atomichub.io.\n- As an additional security measure, make sure you were pinged in ⁠waxwaifus.\n- If you feel insecure, ask a Bouncer or Bodyguard in our main chat.\nThere is more information about my home collection at <https://waxwaifus.carrd.com/>.\nEnjoy your gift and always feel free to ask any questions, please!\nRemember to claim this link, otherwise all unclaimed links will be reclaimed by The Pink Fairy after 31 days!"""
            await member.send(user_message)
            await ctx.message.add_reaction("📪")    
            log_message = f"User {member.name} received claimlink {claimlink.split('?key')[0]} from {ctx.author.name}. Reason: {memo}"[0:969]
            channel = self.bot.get_channel(settings.LOG_CHANNEL)
            await channel.send(log_message)
            await ctx.message.add_reaction("💌")    
        except Exception as e:
            await ctx.send(f"Ran into an error creating claimlink: {e}\n")

async def setup(bot):
	await bot.add_cog(Drop(bot))