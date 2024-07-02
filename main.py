from dctoken import *
import discord
from discord.ext import commands
from discord import ui
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.load_extension('cogs.admin')
    await bot.load_extension('cogs.gacha')
    await bot.load_extension('cogs.update')
    await bot.load_extension('cogs.rps')
    await bot.load_extension('cogs.raid')

    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')
    asyncio.create_task(update_gacha_loop())
    asyncio.create_task(update_raid_loop())

async def update_gacha_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await bot.get_cog('Update').update_gacha()
        await asyncio.sleep(86400)

async def update_raid_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        await bot.get_cog('Update').update_raid()
        await asyncio.sleep(1800)

bot.run(token_test)