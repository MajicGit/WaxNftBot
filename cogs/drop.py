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
    async def drop(self, ctx, member: discord.Member, memo: str = "Congratulations you've won a random Waifu NFT!"):
        await ctx.message.add_reaction("📬")
        available_assets = (await utils.try_api_request(f"/atomicassets/v1/assets?collection_name=thewaxwaifus&owner={settings.WAX_ACC_NAME}&page=1&limit=1000",endpoints=utils.aa_api_list))['data']
        print(available_assets)
        if len(available_assets) == 0:
            await ctx.send(f"Error sending claimlink: No thewaxwaifu assets in wallet {settings.WAX_ACC_NAME} found")
            return
        to_send = secrets.choice(available_assets)['asset_id']
        
        claimlink = await utils.gen_claimlink([to_send], memo = memo) 
        print(claimlink)

        if "https://wax.atomichub.io/trading/link/" not in claimlink:
             await ctx.send(f"Link generation failed! {claimlink}. Please try again and/or ping Majic")


        user_message = f"Congratulations! You have been sent a random Wax Waifu NFT!\n Use the following link to claim them! {claimlink}\nPlease always make sure that the top level domain of the link is **atomichub.io** and double check that I am the actual Wax Waifu NFT Tipbot"
        await member.send(user_message)
        await ctx.message.add_reaction("📪")    
        print(claimlink)


async def setup(bot):
	await bot.add_cog(Drop(bot))