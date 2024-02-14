import discord
from discord.ext import commands
from typing import Union
import utils 
import settings
import json

async def fetch_schemas(collection_name="thewaxwaifus"):
    r = await utils.try_api_request(f"/atomicassets/v1/schemas?collection_name={collection_name}", endpoints=utils.fast_aa_api_list)
    return r['data']



#Goal: List of dictionary for each template -- card_id, group, schema_name, data, template_ids, attributes 

#Goal: Series for each schema: "series"  -- filter by schema name. 


        # "name": "Location Cards",
        # "group": "dynamic",
        # "schema_name": "location",
        # "data": {},
        # "custom": [
        #   {
        #     "key": "rarity",
        #     "default": null
        #   }

async def query_templates(schema_name,collection_name="thewaxwaifus"):
    r = await utils.try_api_request(f"/atomicassets/v1/templates?collection_name={collection_name}&schema_name={schema_name}&has_assets=true", endpoints=utils.fast_aa_api_list)
    return r['data']


def is_special(template_id):
    id = int(template_id)
    if id == 733834:
        return "Tier One"
    if id in [765691, 765692, 765693]:
        return "Tier Two"
    return "0"

async def gen_schema():
    to_ignore = [738538]
    schemas = [] 
    templates = [] 
    all_schemas = [] 
    for i in await fetch_schemas():
        name = i['schema_name']
        all_schemas.append(name)
        for j in await query_templates(name,"thewaxwaifus"):
            template_id = j['template_id']
            if int(template_id) in to_ignore:
                continue
            try:
                card_name = j['immutable_data']['name']
            except:
                try:
                    card_name = (await utils.try_api_request(f"/atomicmarket/v1/assets?collection_name=thewaxwaifus&template_id={template_id}&page=1&limit=11&order=desc&sort=asset_id", endpoints=utils.fast_aa_api_list))['data'][0]['data']['name'].split("-#")[0]
                except Exception as e:
                    print(e)
                    continue 
            special = is_special(template_id)
            if special == "0":
                card_data = {"name": card_name, "template_ids":[template_id],"schema_name":name,"data":{},"attributes":[]}
            else:
                card_data = {"name": card_name, "group":special, "template_ids":[template_id],"schema_name":name,"data":{},"attributes":[]}
            templates.append(card_data)
        


    done_schemas = ["waxwaifus", "pixelwaifus", "blendurwaifu", "waifucosplay", "waifurewards", "waxwaifupack", "waifuidcards", "waifupromos", "waifucustoms"]

    schemas_alone = [["pixelwaifus", "Pixel Waifus"],["blendurwaifu", "Blendur Waifus"], ["waifucosplay","Waifu Cosplay"], ["waifurewards","Waifu Rewards"], ["waifupromos", "Waifu Promos"], ["waifucustoms", "Waifu Customs"], ["waxwaifupack", "Waifu Packs"], ["waifuidcards", "ID Cards"]] + [[i,i] for i in all_schemas if i not in done_schemas]
    for i in schemas_alone:
        print(i)
        actual_name = i[0]
        display_name = i[1]
        schema_data = {"name":display_name, 
        "filters":[{
            "name": display_name,
            "schema_name": actual_name,
            "data": {},
            "custom": []
        }]}
        schemas.append(schema_data)



    schemas_together = [["Waifus", [["Tier Two", "Tier Two"], ["Tier One", "Tier One"]]]] # ["Moff Moff Dragum!", [["ingame","In game items"],["badge","Badges"],["moff_token","Tokens!"],["special badge","Special Badges!"]]]]

    for i in schemas_together:
        display_name = i[0] 
        filter_list = []
        for j in i[1]:
            group_name = j[0]
            display = j[1] 
            cur_filter = {
                "name": display,
                "data": {},
                "group": group_name,
                "custom": []
            }
            filter_list.append(cur_filter)

        schema_data = {"name":display_name,
            "filters":filter_list}
        schemas.append(schema_data)


    final = {"name": "Wax Waifus", "data":templates, "series":schemas}
    with open("thewaxwaifus.json", "w") as outfile:
        json.dump(final,outfile)



class Schema(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  
        print("Schema cog loaded")
		
    @commands.command(description="Get AH Collection Book.",
                      aliases=["collectionbook"])
    @commands.has_any_role(1138222735827423252, 1137852719328137317, 1019942433485754488)
    async def schema(self, ctx):
        try:
            await ctx.message.add_reaction("👀")
            await gen_schema()
            await ctx.send("Generated Schema File", file=discord.File('thewaxwaifus.json'))    
        except Exception as e:
            await ctx.send(f"Ran into an error {e} please ping Majic\n")

async def setup(bot):
	await bot.add_cog(Schema(bot))