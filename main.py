from dctoken import token
import ui_element
import discord
from discord.ext import commands
from discord import ui

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)



@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

@bot.tree.command(name="shittim-chest", description="啓動シッテムの箱")
async def custom_roles(interaction:discord.Interaction):
    await interaction.response.send_message(embed=ui_element.MainUi().Embed(), view=ui_element.MainUi().View())

@bot.command(name="sync", description="Sync commands")
async def sync(ctx:commands.Context):
    try:
        bot.tree.clear_commands(guild=discord.Object(id=863849091821994014))
        bot.tree.copy_global_to(guild=discord.Object(id=863849091821994014))
        synced = await bot.tree.sync(guild=discord.Object(id=863849091821994014))
        await ctx.send(f"{len(synced)} Commands synced")
    except Exception as e:
        await ctx.send(e)


bot.run(token)