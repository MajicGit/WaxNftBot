WAX_ACC_PRIVKEY = ""
WAX_ACC_NAME = "" #Name of wax account doing the dropping 
WAX_PERMISSION ="active"
DISCORD_BOT_TOKEN = ""
LOG_CHANNEL = 0 #Discord channel in which to log succesful drops 
DAILY_DROP_LIMIT = 100 #Daily drop limit for those with perms 
DROP_ROLES = [] #Roles that are allowed to drop 
react_emoji_sequence = ["📬", "📪", "💌"] #First sent upon command, second when DM is sent, last when logging is complete
BOT_PREFIX = "," #Bot command prefix 
BOT_DESCRIPTION = "NFT Tipbot" #Description of Discord Bot 
DEFAULT_DROP_MEMO = "Congratulations you've won a random NFT!" #Default Drop memo
DROP_EXTRA_INFO = " Remember to claim this link, otherwise all unclaimed links may be reclaimed after 31 days!" #Extra information to include with drop memos 
COLLECTION_NAME = "" #Target collection 


#Default DM message with generated claimlink.

def link_to_message(claimlink):
    return f"""Congratulations, the Pink Fairy sent you a random NFT!\nYou can claim it by clicking the following link (just login with your wax_chain wallet, might require allowing popups): {claimlink}\n**WARNING: Anyone you share this link with can claim it, so, do not share with anyone if you do not want to give the NFT away!**\n__Also, please, avoid scams:__\n- Before clicking a claim link, ensure the top level domain is atomichub.io.\n- As an additional security measure, make sure you were pinged in ⁠waxwaifus.\n- If you feel insecure, ask a Bouncer or Bodyguard in our main chat.\nThere is more information about my home collection at <https://waxwaifus.carrd.com/>.\nEnjoy your gift and always feel free to ask any questions, please!\nRemember to claim this link, otherwise all unclaimed links will be reclaimed by The Pink Fairy after 31 days!\n\nIf you prefer having the Fairy send you NFTs directly to your wallet in the future, you can reply to this with `,setwallet <address>`!"""


def transfer_to_message(asset, tx_id):
    try:
        ipf_link = f"https://atomichub-ipfs.com/ipfs/{asset['data']['img']}"
    except:
        ipf_link = f"https://atomichub-ipfs.com/ipfs/{asset['data']['video']}"
    return f"""Congratulations, the Pink Fairy sent a [random NFT]({ipf_link}) directly to your wallet!\nYou can view your NFT on [AtomicHub](<https://wax.atomichub.io/explorer/asset/wax-mainnet/{asset['asset_id']}>)\nIf you feel insecure, ask a Bouncer or Bodyguard in our main chat.\nThere is more information about my home collection at <https://waxwaifus.carrd.com/>.\nEnjoy your gift and always feel free to ask any questions, please!""" 

GUILD = 0 #Guild ID for chatloot
CHATLOOT_PROBABILITY = 1000 #One in how many messages on average will receive a random drop
CHATLOOT_COOLDOWN = 0 #Cooldown between random chatloots for some person

# AH-Collection Book Schema util:
TEMPLATE_TO_IGNORE = [] #Templates to not include in collection book

#Map between Schema name and name to display in collection book
SCHEMA_NAME_MAP = {"pixelwaifus": "Pixel Waifus"}
#Schemas that are grouped together.
SCHEMAS_GROUPED = {"Waifus": {"Tier Two": "Tier Two", "Tier One": "Tier One"}}

SCHEMA_IGNORE = ["waxwaifus"]

DISPLAY_COLLECTION_NAME = ""

def is_special(template_id):
    """Template IDs for which a custom schema is specified. Return "0" if nothing special."""
    return "0"
