#
#   Purpose: Main file to launch discord bot
#   Created: 09/11/2020
#   Refactored: 10/01/2023
#   Author: Jaicob Schott
#

import os
import json
import interactions

from interactions import Button, ButtonStyle, SelectMenu, Option, OptionType, SelectOption
#from discord.ext import commands

config = json.load(open('config/config.json', 'r'))

client = interactions.Client(
    token=config["bot_token"],
    default_scope=config["guild_id"].split(",")
)

@client.event
async def on_ready():
    await client.change_presence(
        interactions.ClientPresence(
            status=interactions.StatusType.IDLE
        )
    )





##
## Load ./modules/*
##

def load_extensions():
    for root, dirs, files in os.walk('./modules'):
        for filename in files:
            if filename.endswith('.py'):
                curMod = f'{os.path.join(root, filename).replace("/", ".")[2:-3]}'
                try:
                    client.load(curMod)
                    print(f'loaded: {curMod}')
                except Exception as e:
                    print(f'failed to load: {curMod}:\n{e}')

##
## module control
##

@client.command(
    name="modulectl",
    description="Module control :P",
    options=[
        Option(
            name="module",
            description="name of module to control",
            type=OptionType.STRING,
            required=True,
        )
    ]
)
async def modSelect(ctx: interactions.CommandContext, module: str):
    buttons = [
        Button(
            style=ButtonStyle.PRIMARY,
            custom_id="load",
            label="load",
        ),
        Button(
            style=ButtonStyle.PRIMARY,
            custom_id="reload",
            label="reload",
        ),
        Button(
            style=ButtonStyle.PRIMARY,
            custom_id="unload",
            label="unload",
        ),
    ]
    await ctx.send(f"Module Control for \"{module}\"", components=[buttons])

@client.component("load")
@client.component("reload")
@client.component("unload")
async def modNameGet(ctx: interactions.ComponentContext):
    # get the name + action of module to work on
    modName = ctx.message.content.split('"')[1::2][0]
    modAction = ctx.data.custom_id

    # now (_|re|un)load the module!
    # depending on the selected function
    try:
        match modAction:
            case "load":
                client.load(f'modules.{modName}')
            case "reload":
                client.reload(f'modules.{modName}')
            case "unload":
                client.remove(f'modules.{modName}')
            case _:
                await ctx.send(f'invalid action name bozo: {modAction}')
                return
            
        await ctx.send(f'{modAction}ing: {modName}')
    except:
        await ctx.send(f'failed to {modAction}: {modName}')

##
## Error Handling
##



##
## Begin
##

def main():
    load_extensions()
    client.start()

if __name__=="__main__":
    main()