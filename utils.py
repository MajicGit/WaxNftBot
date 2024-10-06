import secrets
import asyncio
import json
import time
import aiohttp
from threading import Lock
import random
from typing import List
LIMIT = 1000


# List of various wax RPC endpoints
query_normal_api_list = ['https://hyperion.oiac.io', 'https://wax.blokcrafters.io', 'https://api-wax.eosauthority.com', 'https://waxapi.ledgerwise.io', 'https://api.wax.greeneosio.com', 'https://wax.cryptolions.io', 'https://wax-api.eosiomadrid.io', 'https://api.wax.liquidstudios.io', 'https://wax.eosusa.io', 'https://wax.eosdac.io', 'https://history-wax-mainnet.wecan.dev', 'https://api.waxeastern.cn', 'https://wax.blacklusion.io', 'https://api.wax.alohaeos.com', 'https://wax.eosdublin.io', 'https://apiwax.3dkrender.com']

# eosusa, ledgerwise and eosdac seem to only return limited history, so we don't want to use them in those cases.
normal_api_list_decent_history = ['https://wax.eu.eosamsterdam.net', 'https://wax.blokcrafters.io', 'https://api-wax.eosauthority.com', 'https://api.wax.greeneosio.com', 'https://wax.cryptolions.io', 'https://wax-api.eosiomadrid.io', 'https://api.wax.liquidstudios.io', 'https://history-wax-mainnet.wecan.dev', 'https://api.waxeastern.cn', 'https://api.wax.alohaeos.com', 'https://wax.eosdublin.io', 'https://apiwax.3dkrender.com']

high_limit_list = ['https://wax.blokcrafters.io', 'https://api-wax.eosauthority.com', 'https://api.wax.greeneosio.com', 'https://wax.cryptolions.io', 'https://api.waxeastern.cn', 'https://api.wax.alohaeos.com', 'https://wax.eosdublin.io']
# Candidates for that one, but which returned slightly different results on a small test were: https://wax.eosusa.io https://api.wax.liquidstudios.io https://apiwax.3dkrender.com 'https://wax.eosrio.io 'https://wax.eosdac.io https://wax.dapplica.io 'https://wax.blacklusion.io',

# Atomicassets APIs that are fast
aa_api_list = ['https://aa.wax.blacklusion.io', 'https://atomic3.hivebp.io', 'https://atomic2.hivebp.io', 'https://aa.neftyblocks.com', 'https://aa-wax-public1.neftyblocks.com', 'https://aa.dapplica.io', 'https://api.atomic.greeneosio.com', 'https://wax-atomic-api.eosphere.io', 'https://wax-aa.eosdac.io', 'https://atomic.hivebp.io', 'https://atomic.3dkrender.com', 'https://wax.eosusa.io', 'https://atomic-wax-mainnet.wecan.dev', 'https://wax-atomic.eosiomadrid.io', 'https://wax.api.atomicassets.io', 'https://atomicassets.ledgerwise.io'] #'https://wax-aa.eu.eosamsterdam.net', 
fast_aa_api_list = aa_api_list

# Endpoints that properly support filtering transactions by memos & senders
filter_queries = ['https://wax.blokcrafters.io', 'https://api-wax.eosauthority.com', 'https://api.wax.greeneosio.com', 'https://wax.cryptolions.io', 'https://history-wax-mainnet.wecan.dev', 'https://api.waxeastern.cn', 'https://apiwax.3dkrender.com', 'https://api.wax.alohaeos.com', 'https://wax.eosdublin.io']
# Candidates that at least returned something for the query: https://wax.dapplica.io https://wax.eosusa.io  https://api.wax.liquidstudios.io 'https://wax.eosdac.io',  'https://wax.blacklusion.io', 'https://wax.eosphere.io',

# These work well with transfers to/from but not with memos
filter_no_memo = ['https://wax.blokcrafters.io', 'https://api-wax.eosauthority.com', 'https://api.wax.greeneosio.com', 'https://wax.cryptolions.io', 'https://history-wax-mainnet.wecan.dev', 'https://wax.blacklusion.io', 'https://apiwax.3dkrender.com', 'https://api.wax.alohaeos.com', 'https://wax.eosdublin.io']
# Candidates that seemed to return correct thing but answers had gaps: https://wax.eosusa.io https://api.wax.liquidstudios.io 'https://wax.eosdac.io','https://wax.eosphere.io',

filter_high_limit = ['https://api.wax.greeneosio.com', 'https://wax.cryptolions.io', 'https://api.waxeastern.cn', 'https://api-wax.eosauthority.com', 'https://wax.blokcrafters.io', 'https://api.wax.alohaeos.com']  # 'https://wax.eosdac.io', 'https://wax.blacklusion.io', , 'https://wax.eosphere.io'
light_nodes = ['https://eos.light-api.net', 'https://instar.light-api.net', 'https://proton.light-api.net', 'https://telos.light-api.net', 'https://wax.light-api.net', 'https://xec.light-api.net', 'https://testnet-lightapi.eosams.xeos.me']


# Prefer these for e.g. retrieving a transaction as ultimately faster
normal_to_spam = [x for x in query_normal_api_list if x not in high_limit_list]

# How many requests made and how many succesfull. To evaluate API choice.
tried_requests = {}

# Store some statistics about when we last queried the endpoint, and have a mutex.
api_info = {}

####################


# Mutex and ratelimit counters for the endpoints
api_mutex = {}
api_ratelimit = {}
# 3

# Initialize parameters for all our API lists.
for i in query_normal_api_list + fast_aa_api_list + high_limit_list:
    tried_requests[i] = [0, 0]
    api_info[i] = {"last_failed": 0, "last_tried": 0, "mutex": Lock(), "ratelimit": 1}

async def do_request(session, request, post_data=None, timeout: float = 10) -> dict:
    if post_data == None:
        async with session.get(request, timeout=timeout) as response:
            return await response.json(content_type=None)
    else:
        async with session.post(request, json=post_data, timeout=timeout) as response:
            return await response.json(content_type=None)


async def try_api_request(request: str, endpoints=query_normal_api_list, post_body=None, session=None) -> dict:
    """ Function that iterates through a list of specified endpoints and tries the specified request until one of them is succesfull"""
    backoff_factor = 0  # Backoff factor for this request
    if session == None:
        async with aiohttp.ClientSession() as session:
            return await try_api_request(request, endpoints, post_body, session)

    # Pick a random endpoint to start off with
    api_index = secrets.randbelow(len(endpoints))
    while True:  # Until success
        for _ in range(0, len(endpoints)):  # Iterate through all endpoints
            api_index = (api_index + 1) % len(endpoints)
            current_api = endpoints[api_index]
            # Acquire mutex
            api_info[current_api]["mutex"].acquire()
            # Check the ratelimit -- if it's getting large start implementing an exponential backoff strategy.
            ratelimit_current = 15 * (api_info[current_api]["ratelimit"] - 0.75)
            if api_info[current_api]["ratelimit"] > 5:
                ratelimit_current = 60 * 2 ** api_info[current_api]["ratelimit"]  # Do some exponential backoff here.

            # If an API request failed within a certain timeframe or we queried this endpoint within the last second then try with a different endpoint.
            if time.time() - api_info[current_api]["last_failed"] < ratelimit_current or time.time() - api_info[current_api]["last_tried"] < 1:
                api_info[current_api]["mutex"].release()
                continue

            api_info[current_api]["last_tried"] = time.time()
            api_info[current_api]["mutex"].release()
            api_info[current_api]["ratelimit"] += 1
            full_req = current_api + request  # Create our full request
            tried_requests[current_api][0] += 1  # For performance tracking
            try:
                # Use dynamic timeout values. Also larger timeout values for large requests
                timeout = 0.69 + 0.2 * backoff_factor
                if "limit=100" in full_req:
                    timeout += 1.9
                if "limit=1000" in full_req:
                    timeout += 3.8
                data = await do_request(session, full_req, post_body, timeout)
            except Exception as e:
                api_info[current_api]["last_failed"] = time.time()

             #   if e not in [aiohttp.ClientConnectorError, aiohttp.ServerTimeoutError,asyncio.TimeoutError,aiohttp.ContentTypeError,aiohttp.ServerDisconnectedError]:
              #       print("Unexpected exception: ", e)
                continue

            try:
                if data["code"] in [404, 410, 400, 500]:
                    api_info[current_api]["last_failed"] = time.time()
                    continue
                if data["code"] == 400:
                    # This can happen if querying for block they don't know about yet.
                    await asyncio.sleep(2)
                    continue
                print("Request returned: ", data["code"], " is this a reason to fail/retry the request?")
            except:
                pass
            try:
                if data['executed'] != True:
                    api_info[current_api]["last_failed"] = time.time()
                    continue
            except:
                pass
            try:
                if data["success"] != True:
                    api_info[current_api]["last_failed"] = time.time()
                    continue
            except:
                pass
            if data is None:
                continue
            # This one is a big ugly. But just ensures the response is what is expected. Might need to be expanded for new types of requests as well.
            if not "actions" in data.keys() and not "data" in data.keys() and (not "get_creator" in request and not "creator" in data.keys()) and (not "get_created_accounts" in request and not "accounts" in data.keys()) and (request != "/v1/chain/get_info") and post_body == None or post_body != None and not "transactions" in data.keys():
                #                print("Invalid response keys. If this is a new response, please verify", data.keys(),data)
                api_info[current_api]["last_failed"] = time.time()
                continue
            tried_requests[current_api][1] += 1
            api_info[current_api]["ratelimit"] = 1  # Reset ratelimit upon a succesfull request

         #   print(full_req)
            return data

        # If we tried all endpoints and none worked (or we were backing off all of them, then sleep and try again later.)
        if backoff_factor > 50:  # Shouldn't happen unless something is wrong.
            print("We tried all API endpoints and all are rate limiting us. Are you sure this is a valid request?", backoff_factor, request)
        backoff_factor += 1
        await asyncio.sleep(2.5 * backoff_factor)

try:
    from aioeosabi.rpc import ERROR_NAME_MAP
    from aioeosabi import EosTransaction, EosKey, EosJsonRpc, EosAction, EosAccount
    import settings 

    normal_api_list = ["https://wax.pink.gg", "https://wax.eu.eosamsterdam.net", 'https://api.wax.liquidstudios.io', 'https://api.wax.bountyblok.io']
    api_rpc = [EosJsonRpc(url=addr) for addr in normal_api_list]
    account = EosAccount(settings.WAX_ACC_NAME, private_key= settings.WAX_ACC_PRIVKEY)


    async def drop_random_from_wallet(bot, drop_message, member, memo: str, log_additional, emoji_sequences = List[str], account = account, sender = "", additional_auths = []):
        """Picks a random NFT from a wallet and sends that to a user"""
        if sender == "":
            sender = account.name

        available_assets = (await try_api_request(f"/atomicassets/v1/assets?owner={sender}&page=1&limit=1000",endpoints=aa_api_list))['data']
        if len(available_assets) == 0:
            await drop_message.channel.send(f"Error sending NFT: No assets in wallet {sender} found.")
            return
        
        choosen_asset = secrets.choice(available_assets)
        to_send = choosen_asset['asset_id']
        try:
            if str(member.id) in bot.linked_wallets:
                await directly_send_nft(bot = bot, drop_message = drop_message, member = member, assets = [to_send], dropped_asset = choosen_asset, memo =  memo, log_additional =  log_additional, emoji_sequences = emoji_sequences, account = account, sender = sender, additional_auths = additional_auths)
                return 
            
        except Exception as e:
            await drop_message.channel.send(f"Ran into an error directly sending the NFT to linked wallet: {e}\n")
            return
        await send_claimlink_nft(bot = bot, drop_message = drop_message, member = member, assets = [to_send], memo =  memo, log_additional =log_additional, emoji_sequences = emoji_sequences, account = account, sender = sender, additional_auths = additional_auths)



    async def directly_send_nft(bot, drop_message, member, assets: List[int], dropped_asset, memo: str, log_additional, emoji_sequences = List[str], account = account, sender = "", additional_auths = [], ):
        """Directly send a NFT to a members linked discord wallet. Assumes they have a linked wallet"""
        target = bot.linked_wallets[str(member.id)]
        tx_id = await send_asset(asset_ids = assets, receiver = target, memo = memo, account = account, sender = sender, additional_auths = additional_auths)     
        await drop_message.add_reaction(emoji_sequences[0])   
        channel = bot.get_channel(settings.LOG_CHANNEL) 
        log_message = (f"User {member.name} received asset https://wax.atomichub.io/explorer/asset/wax-mainnet/{' '.join(assets)} directly to their wallet https://wax.bloks.io/account/{target}." + log_additional)[0:969]
        await channel.send(log_message) 
        user_message = settings.transfer_to_message(dropped_asset, tx_id)
        await member.send(user_message)
        await drop_message.add_reaction(emoji_sequences[1])
    

    async def send_claimlink_nft(bot, drop_message, member, assets: List[int], memo: str, log_additional, emoji_sequences = List[str], account = account, sender = "", additional_auths = []):
        """Created and DMs a user a claimlink with the specified assets"""
        claimlink = await gen_claimlink(assets, memo = memo + settings.DROP_EXTRA_INFO, account = account, sender = sender, additional_auths = additional_auths)
        print(claimlink)

        if "https://wax.atomichub.io/trading/link/" not in claimlink:
            await drop_message.channel.send(f"Link generation failed! {claimlink}. Please try again and/or ping Majic")
            return
        
        await drop_message.add_reaction(emoji_sequences[0])  
        user_message = settings.link_to_message(claimlink)
        await member.send(user_message)

        channel = bot.get_channel(settings.LOG_CHANNEL)
        log_message = (f"User {member.name} received claimlink <{claimlink.split('?key')[0]}>" + log_additional)[0:969] 
        await channel.send(log_message) 
        await drop_message.add_reaction(emoji_sequences[1])
        

    async def send_asset(asset_ids: List[int], receiver: str, account: EosAccount = account, memo = "", sender = "", additional_auths = []):
        authorization=[account.authorization(settings.WAX_PERMISSION)] + additional_auths
        memo = str(memo)[:256]
        if sender == "":
            sender = account.name
        actions = [
            EosAction(
                    account='atomicassets',
                    name='transfer',
                    authorization=authorization,
                    data={"from": sender, "to": receiver, "asset_ids": asset_ids, "memo": memo},
                )
            ]
        resp, msg = await doAction(actions, api_rpc, account)
        if resp == False:
            raise Exception(f"Failed to send NFT. Error: {msg}")
        tx_id = msg["transaction_id"]
        return tx_id

    async def gen_claimlink(asset_ids: List[int], account: EosAccount = account, memo = "", sender = "", additional_auths = []):
        keypair = EosKey()
        priv_key = keypair.to_wif()
        key = keypair.to_public()
        authorization=[account.authorization(settings.WAX_PERMISSION)] + additional_auths
        memo = str(memo)[:256]
        if sender == "":
            sender = account.name
        actions = [
            EosAction(
                    account='atomictoolsx',
                    name='announcelink',
                    authorization=authorization,
                    data={
                        'creator': sender,
                        'key': key,
                        'asset_ids': asset_ids,
                        'memo': memo
                    }
                ),
            EosAction(
                    account='atomicassets',
                    name='transfer',
                    authorization=authorization,
                    data={"from": sender, "to": "atomictoolsx", "asset_ids": asset_ids, "memo": "link"},
                )
            ]
        resp, msg = await doAction(actions, api_rpc, account)
        if resp == False:
            raise Exception(f"Failed to create claimlink, please try again. Error: {msg}")
        tx_id = msg["transaction_id"]
        try:
            newresp = await try_api_request(f"/v2/history/get_transaction?id={tx_id}", query_normal_api_list)
            if "link_id" not in str(newresp):
                print("Weird - please debug! Error")
                print(newresp)
                newresp = msg 
        except Exception as e:
            print("Exception getting trx", e)
            newresp = msg
        try:
            link_id = str(newresp).split("link_id': '")[1].split("'")[0]
            link = f'https://wax.atomichub.io/trading/link/{link_id}?key={priv_key}'
        except Exception as e:
            print("Exception getting trx", e)
            newresp = msg
            link_id = str(newresp).split("link_id': '")[1].split("'")[0]
            link = f'https://wax.atomichub.io/trading/link/{link_id}?key={priv_key}'
        return link
    
    async def doAction(action_array, api_rpc, account, ref_block={}, index=None, retry = 5):
        """ Very basic helper function to create a transaction """
        if index is None:
            index = (secrets.randbelow(len(api_rpc)) + random.randint(0,5)) % len(api_rpc)
        for i in range(0, retry):
            try:
                rpc = api_rpc[index]
                if len(ref_block) == 0 or i > 0:
                    block = await rpc.get_head_block()
                    ref_block["block_num"] = block['block_num']
                    ref_block["ref_block_prefix"] = block['ref_block_prefix']
                transaction = EosTransaction(
                    ref_block_num=ref_block["block_num"] & 65535,
                    ref_block_prefix=ref_block["ref_block_prefix"],
                    actions=action_array)
                resp = await rpc.sign_and_push_transaction(transaction, keys=[account.key])
                return True, resp
            except Exception as e:
                try:
                    if e.args[0]['code'] == 3050003:
                        try:
                            if "has insufficient ram;" in e.args[0]['details'][0]['message']:
                                return False, "Failed to create claimlink"
                        except:
                            pass
                        print(e)
                        return False, "Unknown error when creating transaction"
                except:
                    print(e)
                print("Failed, will try again; ", i, e)
                if i > 3:
                    await asyncio.sleep(0.19)
                index += 1
                index = index % len(api_rpc)

        return False, "Wax endpoints acting up with creation of transaction"

    async def transfer(from_addr, to_addr, asset_ids, api_rpc, account, memo=""):
        """
        Given a list of asset ids and a target, sends them out.
        """
        while len(asset_ids) > 0:
            action = EosAction(
                account="atomicassets",
                name="transfer",
                authorization=[account.authorization('active')],
                data={"from": from_addr, "to": to_addr, "asset_ids": asset_ids[0:min(423, len(asset_ids))], "memo": memo},
            )
            asset_ids = asset_ids[423:]
            await doAction([action], api_rpc, account)


except Exception as e:
    print(e)
    print("AIOEOS not installed, won't have support for submitting transactions")
