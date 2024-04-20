from dctoken import *
import discord
from discord.ext import commands
from discord import ui

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    await bot.load_extension('cogs.admin')
    await bot.load_extension('cogs.gacha')
    await bot.load_extension('cogs.update')
    await bot.load_extension('cogs.rps')

    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

bot.run(token_test)