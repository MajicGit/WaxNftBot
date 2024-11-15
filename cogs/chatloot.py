from discord.ext import commands
import settings
import secrets
import time
import utils


class Chatloot(commands.Cog):
    """
    Chatloot Cog:
    Enables randomly dropping *non-spam* messages with some probabilitiy
    And provides a command by which the probability can be reduced until the next message.
    """

    def __init__(self, bot):
        self.bot = bot
        self.last_seen_messages = []
        self.last_seen_users = {}
        self.last_dropped_time = {}
        self.winning_probability = settings.CHATLOOT_PROBABILITY
        print("Chatloot cog loaded")

    def is_spam(self, message, author):
        """Checks a few properties of the message in order to (hopefully) not drop spammy messages"""
        msg_time = int(time.time())
        quality_message = True
        if message in self.last_seen_messages:
            quality_message = False
        if author in self.last_seen_users:
            if msg_time - self.last_seen_users[author] < 120:
                quality_message = False
        message_split = message.lower().split(" ")
        reasonable = set(i for i in message_split if len(i) > 3)
        if len(reasonable) < 2:
            quality_message = False
        if quality_message:
            if author in self.last_seen_users:
                self.last_seen_users[author] = msg_time
            else:
                if len(self.last_seen_users) >= 30:
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
            if message.author.bot:
                return
            userid = message.author.id
            if self.is_spam(message.content, userid):
                return
            if userid in self.last_dropped_time and self.last_dropped_time[
                userid
            ] + settings.CHATLOOT_COOLDOWN > int(time.time()):
                return
            if secrets.randbelow(self.winning_probability) != 1:
                return
            # If probability was adjusted due to command, make sure it's reset
            self.winning_probability = settings.CHATLOOT_PROBABILITY
            self.last_dropped_time[userid] = int(time.time())
            await message.add_reaction(settings.react_emoji_sequence[0])
            log_additional = f" Drop due to random chat activity"
            memo = "Congratulations! You've been randomly chosen to receive an NFT!"
            await utils.drop_random_from_wallet(
                bot=self.bot,
                drop_message=message,
                member=message.author,
                memo=memo,
                log_additional=log_additional,
                emoji_sequences=settings.react_emoji_sequence[1:],
            )
        except Exception as e:
            await message.channel.send(
                f"Ran into an error. Please ping {settings.MAINTAINER}!: {e}\n"
            )

    @commands.command(
        description="Increase probability of chatloot until next drop occurs.",
        aliases=["randomloot"],
    )
    @commands.has_any_role(*settings.DROP_ROLES)
    async def chatlootdrop(self, ctx, probability: str):
        try:
            await ctx.message.add_reaction(settings.react_emoji_sequence[0])
            # Check user has drops available
            try:
                int_proba = int(probability)
            except:
                await ctx.send(
                    f"Error adjusting probability {probability} isn't a valid natural number"
                )
            if ctx.author.id not in self.bot.drops_used:
                self.bot.drops_used[ctx.author.id] = set()
            filtered_timestamps = {
                ts
                for ts in self.bot.drops_used[ctx.author.id]
                if ts >= time.time() - (24 * 60 * 60)
            }
            self.bot.drops_used[ctx.author.id] = filtered_timestamps
            if len(self.bot.drops_used[ctx.author.id]) > settings.DAILY_DROP_LIMIT:
                await ctx.send(
                    f"Error adjusting probability: You've used up your daily limit."
                )
            self.bot.drops_used[ctx.author.id].add(int(time.time()))

            # Adjust probability
            self.winning_probability = max(int_proba, 2)
            await ctx.message.add_reaction(settings.react_emoji_sequence[2])
            await ctx.message.delete()
        except Exception as e:
            await ctx.send(
                f"Ran into an error. Please ping {settings.MAINTAINER}!: {e}\n"
            )


async def setup(bot):
    await bot.add_cog(Chatloot(bot))
