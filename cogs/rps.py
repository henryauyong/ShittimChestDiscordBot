import random

import discord
from discord import app_commands
from discord.ext import commands

game_states = {}


def get_winner(interaction: discord.Interaction):
    players = [*game_states[interaction.message.id].keys()]
    player1 = game_states[interaction.message.id][players[0]]
    player2 = game_states[interaction.message.id][players[1]]

    embed = LobbyEmbed(players[0], players[1], "遊戲結束")

    if player1 is None or player2 is None:
        return None
    if player1 == player2:
        embed.add_field(value="**平手！**", name="\u200b")
        return embed

    if player1 == "rock":
        winner = f'<@{(players[1] if player2 == "paper" else players[0])}>'

    elif player1 == "paper":
        winner = f'<@{(players[1] if player2 == "scissors" else players[0])}>'

    elif player1 == "scissors":
        winner = f'<@{(players[1] if player2 == "rock" else players[0])}>'

    if "-1" in winner:
        winner = "彩奈"

    embed.add_field(value=f"**{winner} 贏了！**", name="\u200b")
    return embed


class LobbyEmbed(discord.Embed):
    def __init__(self, author: discord.User.id, opponent: discord.User.id, status):
        super().__init__(title=status, color=discord.Color.green())
        self.add_field(name="玩家1", value=f"<@{author}>", inline=True)
        if opponent is None:
            self.add_field(name="玩家2", value="等待對手中...", inline=True)
        elif opponent == -1:
            self.add_field(name="玩家2", value="彩奈", inline=True)
        else:
            self.add_field(name="玩家2", value=f"<@{opponent}>", inline=True)


class GameView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.message = None
        self.add_item(self.RockButton())
        self.add_item(self.PaperButton())
        self.add_item(self.ScissorsButton())

    class RockButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="✊", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            game_states[interaction.message.id][interaction.user.id] = "rock"
            embed = get_winner(interaction)
            if embed is not None:
                await interaction.response.edit_message(embed=embed, view=None)
                game_states.pop(interaction.message.id)
            else:
                await interaction.response.send_message("你出了石頭！", ephemeral=True)

    class PaperButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="✋", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            game_states[interaction.message.id][interaction.user.id] = "paper"
            embed = get_winner(interaction)
            if embed is not None:
                await interaction.response.edit_message(embed=embed, view=None)
                game_states.pop(interaction.message.id)
            else:
                await interaction.response.send_message("你出了布！", ephemeral=True)

    class ScissorsButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="✌️", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            game_states[interaction.message.id][interaction.user.id] = "scissors"
            embed = get_winner(interaction)
            if embed is not None:
                await interaction.response.edit_message(embed=embed, view=None)
                game_states.pop(interaction.message.id)
            else:
                await interaction.response.send_message("你出了剪刀！", ephemeral=True)

    async def on_timeout(self):
        try:
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)
        except discord.NotFound:
            pass


class FindOpponentView(discord.ui.View):
    def __init__(self, author: discord.User):
        super().__init__()
        self.author = author
        self.message = None
        self.add_item(self.JoinButton())
        self.add_item(self.CancelButton())

    class JoinButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="加入", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            if interaction.user == self.view.author:
                await interaction.response.send_message(
                    "你不能跟自己玩！", ephemeral=True
                )
            else:
                view = GameView()
                embed = LobbyEmbed(
                    self.view.author.id, interaction.user.id, "遊戲進行中"
                )
                await interaction.response.edit_message(embed=embed, view=view)
                view.message = await interaction.original_response()
                state = {self.view.author.id: None, interaction.user.id: None}
                game_states[interaction.message.id] = state

    class CancelButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="取消", style=discord.ButtonStyle.danger)

        async def callback(self, interaction: discord.Interaction):
            if interaction.user == self.view.author:
                await interaction.message.delete()
            else:
                await interaction.response.send_message(
                    "只有發起者可以取消！", ephemeral=True
                )

    async def on_timeout(self):
        try:
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)
        except discord.NotFound:
            pass


class ChooseOpponentView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.message = None
        self.add_item(self.PvpButton())
        self.add_item(self.PvEButton())

    class PvpButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="其他老師", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            view = FindOpponentView(interaction.user)
            embed = LobbyEmbed(interaction.user.id, None, "等待對手中...")
            await interaction.response.send_message(view=view, embed=embed)
            view.message = await interaction.original_response()
            await interaction.followup.delete_message(interaction.message.id)

    class PvEButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="彩奈", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            view = GameView()
            embed = LobbyEmbed(interaction.user.id, -1, "遊戲進行中")
            choices = ["rock", "paper", "scissors"]
            state = {interaction.user.id: None, -1: random.choice(choices)}
            await interaction.response.send_message(embed=embed, view=view)
            view.message = await interaction.original_response()
            game_states[view.message.id] = state
            await interaction.followup.delete_message(interaction.message.id)

    async def on_timeout(self):
        try:
            for item in self.children:
                item.disabled = True
            await self.message.edit(view=self)
        except discord.NotFound:
            pass


class Rps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="rps", description="來猜拳吧！")
    async def rps(self, interaction: discord.Interaction):
        embed = discord.Embed(title="老師要跟誰玩呢？", color=discord.Color.green())
        view = ChooseOpponentView()

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.message = await interaction.original_response()


async def setup(bot: commands.Bot):
    await bot.add_cog(Rps(bot))
