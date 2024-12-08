from discord.ext import commands
import settings
import secrets
import discord
import settings
from datetime import date
import datetime
import utils
from aioeosabi import EosAccount
import datetime


class TrickOrTreat(commands.Cog):
    """
    Trick Or Treat Cog
    Cog that gives users a daily command they can use.
    Use will either: times them out, sends them a drop from a special wallet and if lucky also send a normal drop.
    """

    def __init__(self, bot):
        self.bot = bot
        self.used_treat = {}
        self.last_timeouts = {}
        print("Trick o Treat cog loaded")

    @commands.command(
        description="Test your luck, you may just win a NFT.",
        aliases=["santa", "trick"],
    )
    @commands.check(lambda ctx: ctx.guild and ctx.guild.id == settings.GUILD)
    @commands.has_any_role(*settings.TRICK_OR_TREAT_ROLES)  # Verified role
    async def trickortreat(self, ctx):
        if ctx.channel.id != settings.TRICK_OR_TREAT_CHANNEL:
            return

        special_wallet = EosAccount(
            settings.TRICK_OR_TREAT_WALLET, private_key=settings.WAX_ACC_PRIVKEY
        )

        userid = ctx.author.id

        # current_time = int(datetime.datetime.timestamp(datetime.datetime.now()))
        if userid in self.used_treat and self.used_treat[
            userid
        ] == date.today().strftime("%d-%m"):
            # 4h Cooldown: if userid in self.used_treat and current_time - self.used_treat[userid] < 60 * 60 * 4 :
            await ctx.message.add_reaction("🕐")
            await ctx.channel.send(
                "You've already tried your luck today! Come back tomorrow"
            )
            # 4h Cooldown: await ctx.channel.send("You've already tried your luck in the past four hours! Come back later")
            return
        self.used_treat[userid] = date.today().strftime("%d-%m")
        # 4h Cooldown: self.used_treat[userid] = current_time
        await ctx.message.add_reaction(settings.TRICK_OR_TREAT_EMOJIS[0])

        randomness = secrets.randbelow(100)

        if (
            len([role.id for role in ctx.author.roles if role.id in settings.TRICK_OR_TREAT_LUCKY_ROLES]) > 1
            and randomness < settings.TRICK_OR_TREAT_BONUS_ODDS
        ):
            # Lucky role: 10% chance to get a normal drop
            await ctx.channel.send(settings.TRICK_OR_TREAT_BONUS_MESSAGE)

            log_additional = settings.TRICK_OR_TREAT_BONUS_LOG
            try:
                await utils.drop_random_from_wallet(
                    bot=self.bot,
                    drop_message=ctx.message,
                    member=ctx.author,
                    memo=settings.TRICK_OR_TREAT_BONUS_MESSAGE,
                    log_additional=log_additional,
                    emoji_sequences=settings.TRICK_OR_TREAT_BONUS_EMOJIS,
                )
            except Exception as e:
                print(f"Ran into an error. Please ping {settings.MAINTAINER}!")
                print(e)

        elif randomness < settings.TRICK_OR_TREAT_TIMEOUT_ODDS:
            timeout_duration = secrets.randbelow(300) + 15
            timeout = 0
            #if userid in self.last_timeouts:
            #    timeout = self.last_timeouts[userid] ** 2 // 60
            await ctx.message.add_reaction(settings.TRICK_OR_TREAT_EMOJIS[1])
            await ctx.channel.send(settings.TRICK_OR_TREAT_TRICK_MESSAGE)
            try:
                await ctx.author.timeout(
                    discord.utils.utcnow()
                    + datetime.timedelta(seconds=timeout_duration + timeout),
                    reason=settings.TRICK_OR_TREAT_TRICK_MESSAGE,
                )
                self.last_timeouts[userid] = timeout_duration
            except Exception as e:
                print("Failed to timeout user", e)
            return
        try:
            self.last_timeouts[userid] = 0
            log_additional = settings.TRICK_OR_TREAT_LOG_MESSAGE
            await utils.drop_random_from_wallet(
                bot=self.bot,
                drop_message=ctx.message,
                member=ctx.author,
                memo=settings.TRICK_OR_TREAT_MEMO,
                log_additional=log_additional,
                emoji_sequences=settings.TRICK_OR_TREAT_EMOJIS[2:],
                account=special_wallet,
            )

        except Exception as e:
            await ctx.send(
                f"Ran into an error. Please ping {settings.MAINTAINER}!: {e}\n"
            )
            self.used_treat[userid] = ""


async def setup(bot):
    await bot.add_cog(TrickOrTreat(bot))
