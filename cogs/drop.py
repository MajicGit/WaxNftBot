import discord
from discord.ext import commands
import utils 
import settings
import secrets
import time 

class Drop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.drops_used = {}
        print("Drop cog loaded")
		
    @commands.command(description="Send the specified discord user a claim link with a random NFT per DM.",
                      aliases=["loot","reward"])
    @commands.has_any_role(*settings.DROP_ROLES)
    async def drop(self, ctx, member: discord.Member, *, memo: str = settings.DEFAULT_DROP_MEMO):
        try:
            await ctx.message.add_reaction(settings.react_emoji_sequence[0])
            #Check user has drops available
            if ctx.author.id not in self.drops_used:
                 self.drops_used[ctx.author.id] = set()
            filtered_timestamps = {ts for ts in self.drops_used[ctx.author.id] if ts >= time.time() - (24*60*60)}
            self.drops_used[ctx.author.id]  = filtered_timestamps
            if len(self.drops_used[ctx.author.id]) > settings.DAILY_DROP_LIMIT:
                 await ctx.send(f"Error sending claimlink: You've used up your daily limit.")
            self.drops_used[ctx.author.id].add(int(time.time()))
            
            available_assets = (await utils.try_api_request(f"/atomicassets/v1/assets?owner={settings.WAX_ACC_NAME}&page=1&limit=1000",endpoints=utils.aa_api_list))['data']
            if len(available_assets) == 0:
                await ctx.send(f"Error sending claimlink: No assets in wallet {settings.WAX_ACC_NAME} found.")
                return
            to_send = secrets.choice(available_assets)['asset_id']
            
            claimlink = await utils.gen_claimlink([to_send], memo = memo + settings.DROP_EXTRA_INFO) 
            print(claimlink)

            if "https://wax.atomichub.io/trading/link/" not in claimlink:
                await ctx.send(f"Link generation failed! {claimlink}. Please try again and/or ping Majic")

            user_message = settings.link_to_message(claimlink)
            await member.send(user_message)
            await ctx.message.add_reaction(settings.react_emoji_sequence[1])    
            log_message = f"User {member.name} received claimlink {claimlink.split('?key')[0]} from {ctx.author.name}. Reason: {memo}"[0:969]
            channel = self.bot.get_channel(settings.LOG_CHANNEL)
            await channel.send(log_message)
            await ctx.message.add_reaction(settings.react_emoji_sequence[2])    
        except Exception as e:
            await ctx.send(f"Ran into an error creating claimlink: {e}\n")

async def setup(bot):
	await bot.add_cog(Drop(bot))