# General Setup:
WAX_ACC_PRIVKEY = ""  # Private key for wax account to use.
WAX_ACC_NAME = ""  # Name of wax account doing the dropping
WAX_PERMISSION = "active"  # Permissions used for dropping.
DISCORD_BOT_TOKEN = ""  # Discord bot token
LOG_CHANNEL = 0  # Discord channel in which to log drops and other log items
BOT_PREFIX = ","  # Bot command prefix
BOT_DESCRIPTION = "NFT Tipbot"  # Description of Discord Bot
DEFAULT_DROP_MEMO = "Congratulations you've won a random NFT!"  # Default Drop memo
DROP_EXTRA_INFO = " Remember to claim this link, otherwise all unclaimed links may be reclaimed after 31 days!"  # Extra information to include with drop memos
COLLECTION_NAME = ""  # Target collection
MAINTAINER = "Majic"  # Your name here

# Drop Settings
DAILY_DROP_LIMIT = 100  # Daily drop limit for those with perms
DROP_ROLES = []  # Roles that are allowed to drop
react_emoji_sequence = [
    "📬",
    "📪",
    "💌",
]  # First sent upon command, second when DM is sent, last when logging is complete

cogs_to_load = [
        "cogs.drop",
        "cogs.collectionbook",
        "cogs.chatloot",
        "cogs.util",
        "cogs.trickortreat",
] # Cogs to load


# Message that is sent with a claimlink
def link_to_message(claimlink):
    return f"""Congratulations, the Pink Fairy sent you a random NFT!\nYou can claim it by clicking the following link (just login with your wax_chain wallet, might require allowing popups): {claimlink}\n**WARNING: Anyone you share this link with can claim it, so, do not share with anyone if you do not want to give the NFT away!**\n__Also, please, avoid scams:__\n- Before clicking a claim link, ensure the top level domain is atomichub.io.\n- As an additional security measure, make sure you were pinged in ⁠waxwaifus.\n- If you feel insecure, ask a Bouncer or Bodyguard in our main chat.\nThere is more information about my home collection at <https://waxwaifus.carrd.com/>.\nEnjoy your gift and always feel free to ask any questions, please!\nRemember to claim this link, otherwise all unclaimed links will be reclaimed by The Pink Fairy after 31 days!\n\nIf you prefer having the Fairy send you NFTs directly to your wallet in the future, you can reply to this with `,setwallet <address>`! For example if your address is `thepinkfairy` then `,setwallet thepinkfairy`"""


# Message that is sent when an NFT is transfered directly
def transfer_to_message(asset, tx_id):
    try:
        ipf_link = f"https://atomichub-ipfs.com/ipfs/{asset['data']['img']}"
    except:
        ipf_link = f"https://atomichub-ipfs.com/ipfs/{asset['data']['video']}"
    return f"""Congratulations, the Pink Fairy sent a [random NFT]({ipf_link}) directly to your wallet!\nYou can view your NFT on [AtomicHub](<https://wax.atomichub.io/explorer/asset/wax-mainnet/{asset['asset_id']}>)\nIf you feel insecure, ask a Bouncer or Bodyguard in our main chat.\nThere is more information about my home collection at <https://waxwaifus.carrd.com/>.\nEnjoy your gift and always feel free to ask any questions, please!"""


# Chatloot Config:
GUILD = 0  # Guild ID for chatloot
CHATLOOT_PROBABILITY = (
    1000  # One in how many messages on average will receive a random drop
)
CHATLOOT_COOLDOWN = 60 * 60 * 24  # Cooldown between chatloots going to same person

# Trick or Treat Config:
TRICK_OR_TREAT_ROLES = []  # Role ID allowed to perform trick or treat
TRICK_OR_TREAT_LUCKY_ROLES = [] # Role ID with better odds and that may receive a normal drop
TRICK_OR_TREAT_CHANNEL = 0  # Channel ID in which trick or treat is used
TRICK_OR_TREAT_WALLET = (
    "waifustreats"  # Wallet from which trick or treat rewards are sent
)
TRICK_OR_TREAT_BONUS_EMOJIS = [
    "<:businessbebe:1139294276065439745>",
    "<:waifustonks:1212006102787555430>",
]  # Emojis that are additionally reacted upon trickortreat if lucky drop.

# AH-Collection Book Schema util:
TEMPLATE_TO_IGNORE = []  # Templates to not include in collection book

# Map between Schema name and name to display in collection book, if unspecified will use schema name.
SCHEMA_NAME_MAP = {"pixelwaifus": "Pixel Waifus"}
# Schemas that are grouped together.
SCHEMAS_GROUPED = {"Waifus": {"Tier Two": "Tier Two", "Tier One": "Tier One"}}
# Schemas not included
SCHEMA_IGNORE = ["waxwaifus"]

DISPLAY_COLLECTION_NAME = "Wax Waifus"


def is_special(template_id):
    """Template IDs for which a custom schema is specified. Return "0" if nothing special."""
    return "0"
