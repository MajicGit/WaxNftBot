import discord
from discord.ext import commands
from typing import Union
import utils 
import settings
import json

async def fetch_schemas(collection_name=settings.COLLECTION_NAME):
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

async def query_templates(schema_name,collection_name=settings.COLLECTION_NAME):
    r = await utils.try_api_request(f"/atomicassets/v1/templates?collection_name={collection_name}&schema_name={schema_name}&has_assets=true", endpoints=utils.fast_aa_api_list)
    return r['data']



async def gen_schema():
    to_ignore = settings.TEMPLATE_TO_IGNORE
    schemas = [] 
    templates = [] 
    all_schemas = [] 
    for i in await fetch_schemas():
        name = i['schema_name']
        all_schemas.append(name)
        for j in await query_templates(name, settings.COLLECTION_NAME):
            template_id = j['template_id']
            if int(template_id) in to_ignore:
                continue
            try:
                card_name = j['immutable_data']['name']
            except:
                try:
                    card_name = (await utils.try_api_request(f"/atomicmarket/v1/assets?collection_name={settings.COLLECTION_NAME}&template_id={template_id}&page=1&limit=11&order=desc&sort=asset_id", endpoints=utils.fast_aa_api_list))['data'][0]['data']['name'].split("-#")[0]
                except Exception as e:
                    print(e)
                    continue 
            special = settings.is_special(template_id)
            if special == "0":
                card_data = {"name": card_name, "template_ids":[template_id],"schema_name":name,"data":{},"attributes":[]}
            else:
                card_data = {"name": card_name, "group":special, "template_ids":[template_id],"schema_name":name,"data":{},"attributes":[]}
            templates.append(card_data)
        


    schemas_alone = list(settings.SCHEMA_NAME_MAP.items()) + [[i,i] for i in all_schemas if i not in settings.SCHEMA_NAME_MAP and i not in settings.SCHEMAS_GROUPED]
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



    for i in settings.SCHEMAS_GROUPED:
        display_name = i
        filter_list = []
        for j in settings.SCHEMAS_GROUPED[i]:
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


    final = {"name": settings.DISPLAY_COLLECTION_NAME, "data":templates, "series":schemas}
    with open(f"{settings.COLLECTION_NAME}_schema.json", "w") as outfile:
        json.dump(final,outfile)



class Schema(commands.Cog):
    def __init__(self, bot):
        self.bot = bot  
        print("Schema cog loaded")
		
    @commands.command(description="Get AH Collection Book",
                      aliases=["collectionbook"])
    @commands.has_any_role(*settings.DROP_ROLES)
    async def schema(self, ctx):
        try:
            await ctx.message.add_reaction("👀")
            await gen_schema()
            await ctx.send("Generated Schema File", file=discord.File(f"{settings.COLLECTION_NAME}_schema.json"))    
            await ctx.message.add_reaction("✔️")
        except Exception as e:
            await ctx.send(f"Ran into an error {e} please ping Majic\n")

async def setup(bot):
	await bot.add_cog(Schema(bot))