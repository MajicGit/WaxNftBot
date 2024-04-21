from discord.ext import commands
import settings
import secrets
import time 



import discord
from discord.ext import commands
from typing import Union
import utils 
import settings
import json



class Chatloot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot          
        self.last_seen_messages = []
        self.last_seen_users = {}
        self.last_dropped_time = {}
        print("Chatloot cog loaded")

    def is_spam(self, message, author):
        msg_time = int(time.time())
        quality_message = True 
        if message in self.last_seen_messages:
            quality_message = False
        if author in self.last_seen_users:
            if msg_time - self.last_seen_users[author] < 120:
                quality_message = False
                msg_time = self.last_seen_users[author]
        message_split = message.lower().split(" ")
        reasonable = set(i for i in message_split if len(i) > 3)
        if len(reasonable) < 2:
            quality_message = False
        if quality_message:
            if author in self.last_seen_users:
                self.last_seen_users[author] = msg_time
            else:
                if len(self.last_seen_users) >= 10:
                    to_remove = next(iter(self.last_seen_users))
                    self.last_seen_users.pop(to_remove)
                self.last_seen_users[author] = msg_time
        if len(self.last_seen_messages) >= 50:
            self.last_seen_messages = self.last_seen_messages[1:]
        self.last_seen_messages.append(message)
        return not quality_message

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            try:
                if message.channel.guild.id != settings.GUILD:
                    return 
            except:
                return
            userid = message.author.id
            if self.is_spam(message.content, userid):
                return 
            if userid in self.last_dropped_time and self.last_dropped_time[userid] + settings.CHATLOOT_COOLDOWN > int(time.time()):
                return   
            if secrets.randbelow(settings.CHATLOOT_PROBABILITY) != 1:
                return 
            self.last_dropped_time[userid] = int(time.time())
            await message.add_reaction(settings.react_emoji_sequence[0])
            available_assets = (await utils.try_api_request(f"/atomicassets/v1/assets?owner={settings.WAX_ACC_NAME}&page=1&limit=1000",endpoints=utils.aa_api_list))['data']
            if len(available_assets) == 0:
                await message.channel.send(f"Error sending claimlink: No assets in wallet {settings.WAX_ACC_NAME} found.")
                return
            print("Chatloot drop!")
            to_send = secrets.choice(available_assets)['asset_id']
            memo = "Congratulations! You've been randomly chosen to receive an NFT!"
            claimlink = await utils.gen_claimlink([to_send], memo = memo + settings.DROP_EXTRA_INFO) 
            print(claimlink)

            if "https://wax.atomichub.io/trading/link/" not in claimlink:
                await message.channel.send(f"Link generation failed! {claimlink}. Please try again and/or ping Majic")
            user_message = settings.link_to_message(claimlink)
            await message.author.send(user_message)
            await message.add_reaction(settings.react_emoji_sequence[1])    
            log_message = f"User {message.author.name} received claimlink {claimlink.split('?key')[0]} from random chat activity."[0:969]
            channel = self.bot.get_channel(settings.LOG_CHANNEL)
            await channel.send(log_message)
            await message.add_reaction(settings.react_emoji_sequence[2])     
        except Exception as e:
            await message.channel.send(f"Ran into an error. Please ping Majic!: {e}\n")



async def setup(bot):
	await bot.add_cog(Chatloot(bot))

#Track last 50 seen messages, last 10 seen users and filter out any duplicates.

