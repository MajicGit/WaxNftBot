import discord
from discord.ext import commands
import utils
import settings
import time
from aioeosabi import EosAccount


class Drop(commands.Cog):
    """
    Drops Cog:
    Enables certain roles to make the bot create and DM a user a claimlink.
    """

    def __init__(self, bot):
        self.bot = bot
        bot.drops_used = {}
        print("Drop cog loaded")

    @commands.command(
        description="Send the specified discord user a claim link with a random NFT per DM.",
        aliases=["loot", "reward"],
    )
    @commands.has_any_role(*settings.DROP_ROLES)
    async def drop(
        self, ctx, member: discord.Member, *, memo: str = settings.DEFAULT_DROP_MEMO
    ):
        try:
            await ctx.message.add_reaction(settings.react_emoji_sequence[0])
            # Check user has drops available
            if ctx.author.id not in self.bot.drops_used:
                self.bot.drops_used[ctx.author.id] = set()
            filtered_timestamps = {
                ts
                for ts in self.bot.drops_used[ctx.author.id]
                if ts >= time.time() - (24 * 60 * 60)
            }
            self.bot.drops_used[ctx.author.id] = filtered_timestamps
            if len(self.bot.drops_used[ctx.author.id]) > settings.DAILY_DROP_LIMIT:
                await ctx.send(f"Error sending NFT: You've used up your daily limit.")
            self.bot.drops_used[ctx.author.id].add(int(time.time()))

            log_additional = f" Drop from {ctx.author.name}. Reason: {memo}"
            await utils.drop_random_from_wallet(
                bot=self.bot,
                drop_message=ctx.message,
                member=member,
                memo=memo,
                log_additional=log_additional,
                emoji_sequences=settings.react_emoji_sequence[1:],
            )

        except Exception as e:
            await ctx.send(f"Ran into an error dropping: {e}\n")

    @commands.command(
        description=f"Send the specified discord user a claim link with a random NFT per DM from a special wallet.",
        aliases=["rumbledrop"],
    )
    @commands.has_any_role(*settings.DROP_ROLES)
    async def stab(
        self, ctx, member: discord.Member, *, memo: str = settings.DEFAULT_DROP_MEMO
    ):
        # This command uses the standard wallets drop perm to authorize the drop from the stab wallet. May require some tweaking
        special_wallet = settings.WAX_STAB_ACC_NAME
        special_auth = [EosAccount(special_wallet).authorization("active")]
        try:
            await ctx.message.add_reaction(settings.react_emoji_sequence[0])
            # Check user has drops available
            if ctx.author.id not in self.bot.drops_used:
                self.bot.drops_used[ctx.author.id] = set()
            filtered_timestamps = {
                ts
                for ts in self.bot.drops_used[ctx.author.id]
                if ts >= time.time() - (24 * 60 * 60)
            }
            self.bot.drops_used[ctx.author.id] = filtered_timestamps
            if len(self.bot.drops_used[ctx.author.id]) > settings.DAILY_DROP_LIMIT:
                await ctx.send(f"Error sending NFT: You've used up your daily limit.")
            self.bot.drops_used[ctx.author.id].add(int(time.time()))

            log_additional = f" Stab from {ctx.author.name}. Reason: {memo}"

            await utils.drop_random_from_wallet(
                bot=self.bot,
                drop_message=ctx.message,
                member=member,
                memo=memo,
                log_additional=log_additional,
                emoji_sequences=settings.react_emoji_sequence[1:],
                sender=special_wallet,
                additional_auths=special_auth,
            )

        except Exception as e:
            await ctx.send(f"Ran into an error dropping: {e}\n")


async def setup(bot):
    await bot.add_cog(Drop(bot))
