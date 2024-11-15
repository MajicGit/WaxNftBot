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
    @commands.has_any_role(settings.TRICK_OR_TREAT_ROLE)  # Verified role
    async def trickortreat(self, ctx):
        if ctx.channel.id != settings.TRICK_OR_TREAT_CHANNEL:
            return

        special_wallet = EosAccount(
            settings.TRICK_OR_TREAT_WALLET, private_key=settings.WAX_ACC_PRIVKEY
        )

        userid = ctx.author.id

        current_time = int(datetime.datetime.timestamp(datetime.datetime.now()))
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
        await ctx.message.add_reaction("🏡")

        randomness = secrets.randbelow(100)

        if (
            settings.TRICK_OR_TREAT_LUCKY_ROLE in [role.id for role in ctx.author.roles]
            and randomness < 10
        ):
            # Lucky role: 10% chance to get a normal drop
            await ctx.channel.send("Bonus Prize! Enjoy a pink fairy NFT drop")

            log_additional = f" Lucky trick or treat bonus drop!"
            try:
                await utils.drop_random_from_wallet(
                    bot=self.bot,
                    drop_message=ctx.message,
                    member=ctx.author,
                    memo="Bonus Treat! You've won a random Waifu NFT",
                    log_additional=log_additional,
                    emoji_sequences=settings.TRICK_OR_TREAT_BONUS_EMOJIS,
                )
            except Exception as e:
                print(f"Ran into an error. Please ping {settings.MAINTAINER}!")
                print(e)

        elif randomness < 25:
            # 25% chance (or 15% for lucky role members) for a timeout
            timeout_duration = secrets.randbelow(300) + 15
            timeout = 0
            if userid in self.last_timeouts:
                timeout = self.last_timeouts[userid] ** 2 // 60
            await ctx.message.add_reaction("🥚")
            await ctx.channel.send("Trick! You didn't get lucky today!")
            try:
                await ctx.author.timeout(
                    discord.utils.utcnow()
                    + datetime.timedelta(seconds=timeout_duration + timeout),
                    reason="Trick! You didn't get lucky today",
                )
                self.last_timeouts[userid] = timeout_duration
            except Exception as e:
                print("Failed to timeout user", e)
            return
        try:
            self.last_timeouts[userid] = 0
            log_additional = f" Trick or Treat drop from daily command."
            await utils.drop_random_from_wallet(
                bot=self.bot,
                drop_message=ctx.message,
                member=ctx.author,
                memo="Treat! You've won some candy",
                log_additional=log_additional,
                emoji_sequences=["👻", "🍬"],
                account=special_wallet,
            )

        except Exception as e:
            await ctx.send(
                f"Ran into an error. Please ping {settings.MAINTAINER}!: {e}\n"
            )
            self.used_treat[userid] = ""


async def setup(bot):
    await bot.add_cog(TrickOrTreat(bot))
