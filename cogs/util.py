from discord.ext import commands
import utils 
import settings
import secrets
import json 
import re

class Util(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            with open("walletlinks.json","r") as f:
                bot.linked_wallets = json.load(f)
        except Exception as e:
            print(f"Encountered error {e} when loading linked wallets")
        print("Util cog loaded")
		
    @commands.command(description="Fetches a random active from chat.",
                      aliases=["random-active","whoisa"])
    async def randomactive(self, ctx, *,num_messages: int = 91):
        try:
            if num_messages <= 0:
                await ctx.send("Can't fetch negative number of messages.")
                return
            if num_messages > 1919:
                await ctx.send("For efficiency reasons, can fetch max 1919 messages.")
                return
            senders = {}
            seen = -1
            async for message in ctx.channel.history(limit=num_messages + 1):
                #+1 due to deferred response
                seen += 1
                if message.author.bot:
                    continue
                if message.author.id == ctx.author.id:
                    continue
                if message.author.id not in senders:
                    senders[message.author.id] = 0
                senders[message.author.id] += 1

            entries = []
            for user in senders:
                count = 1 + (senders[user]-1) // 10
                for _ in range(count):
                    entries.append(user)
            
            if len(entries) == 0:
                await ctx.send("No valid messages found.")
                return 
            if len(senders) == 1:
                await ctx.send(f"Only a single active user in the last {seen} messages.")
                return 
            winner = entries[secrets.randbelow(len(entries))]
            await ctx.send(f"Random active in the last {seen} messages: <@{winner}>")
        except Exception as e:
            await ctx.send(f"Ran into an error {e}. If this persists please ping Majic")


    @commands.command(description="Register your wallets to receive your NFTs directly.",
                      aliases=["set-wallet", "walletlink" ,"link", "link-wallet", "register"])
    async def setwallet(self, ctx, *, address: str):
        try:
            await ctx.message.add_reaction("👀")    
            regex = r'(^[a-z1-5.]{0,11}[a-z1-5]$)|(^[a-z1-5.]{12}[a-j1-5]$)'
            if not re.match(regex, address):
                await ctx.send("Wax wallet appears to be invalid. Please double check and ping Majic.")
                return
            self.bot.linked_wallets[str(ctx.author.id)] = address
            with open("walletlinks.json","w") as f:
                json.dump(self.bot.linked_wallets, f) 
            log_message = f"User {ctx.author.name} <@{ctx.author.id}> linked to wallet [{address}](<https://wax.bloks.io/account/{address}>)"
            channel = self.bot.get_channel(settings.LOG_CHANNEL)
            await channel.send(log_message)
            await ctx.message.add_reaction("✅")
        except Exception as e:
            await ctx.send(f"Ran into an error {e}. If this persists please ping Majic")

    @commands.command(description="Get your registered wallet.",
                      aliases=["get-wallet", "getlink", "wallet"])
    async def getwallet(self, ctx):
        try:
            if str(ctx.author.id) in self.bot.linked_wallets:
                await ctx.send(f"Your currently linked wallet is {self.bot.linked_wallets[str(ctx.author.id)]}. You can use `,setwallet` to change this or `,clearwallet` to receive claimlinks instead.")
            else:
                await ctx.send("You currently do not have any wallet linked. You can use `,setwallet` to set a wallet")
        except Exception as e:
            await ctx.send(f"Ran into an error {e}. If this persists please ping Majic")


    @commands.command(description="Clear your registered wallet.",
                      aliases=["clear-wallet", "unlink" ,"unregister"])
    async def clearwallet(self, ctx):
        try:
            if str(ctx.author.id) in self.bot.linked_wallets:
                log_message = f"User {ctx.author.name} {ctx.author.id} cleared their wallet"
                self.bot.linked_wallets.pop(str(ctx.author.id))
                channel = self.bot.get_channel(settings.LOG_CHANNEL)
                with open("walletlinks.json","w") as f:
                    json.dump(self.bot.linked_wallets, f) 
                await ctx.send(f"Succesfully cleared your wallet. To set a new wallet, you can use `,setwallet`.")
            else:
                await ctx.send("You currently do not have any wallet linked. You can use `,setwallet` to set a wallet")
        except Exception as e:
            await ctx.send(f"Ran into an error {e}. If this persists please ping Majic")

async def setup(bot):
	await bot.add_cog(Util(bot))