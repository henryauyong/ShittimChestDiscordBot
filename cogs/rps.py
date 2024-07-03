import random

import discord
from discord import app_commands
from discord.ext import commands

game_states = {}


def get_winner(interaction: discord.Interaction):
    players = [*game_states[interaction.message.id].keys()]
    player1 = game_states[interaction.message.id][players[0]]
    player2 = game_states[interaction.message.id][players[1]]
    emoji = {"rock": "✊", "paper": "✋", "scissors": "✌️"}

    if player1 is None or player2 is None:
        return None

    embed = LobbyEmbed(players[0], players[1], "遊戲結束", emoji[player1], emoji[player2])

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

    embed.add_field(value=f"**{winner} 贏了！**", name="結果")
    return embed


class LobbyEmbed(discord.Embed):
    def __init__(self, author: discord.User.id, opponent: discord.User.id, status, player1=None, player2=None):
        super().__init__(title=status, color=discord.Color.green())
        if player1 is not None:
            self.add_field(name="玩家1", value=f"<@{author}>\n{player1}", inline=True)
        else:
            self.add_field(name="玩家1", value=f"<@{author}>", inline=True)


        if opponent is None:
            self.add_field(name="玩家2", value="等待對手中...", inline=True)
        elif opponent == -1:
            if player2 is not None:
                self.add_field(name="玩家2", value=f"彩奈\n{player2}", inline=True)
            else:
                self.add_field(name="玩家2", value="彩奈", inline=True)
        elif player2 is not None:
            self.add_field(name="玩家2", value=f"<@{opponent}>\n{player2}", inline=True)
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
            if interaction.user.id in game_states[interaction.message.id]:
                game_states[interaction.message.id][interaction.user.id] = "rock"
                embed = get_winner(interaction)
                if embed is not None:
                    await interaction.response.edit_message(embed=embed, view=None)
                    game_states.pop(interaction.message.id)
                else:
                    await interaction.response.send_message("你出了石頭！", ephemeral=True)
            else:
                await interaction.response.send_message("你不是這場遊戲的玩家！", ephemeral=True)

    class PaperButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="✋", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id in game_states[interaction.message.id]:
                game_states[interaction.message.id][interaction.user.id] = "paper"
                embed = get_winner(interaction)
                if embed is not None:
                    await interaction.response.edit_message(embed=embed, view=None)
                    game_states.pop(interaction.message.id)
                else:
                    await interaction.response.send_message("你出了布！", ephemeral=True)
            else:
                await interaction.response.send_message("你不是這場遊戲的玩家！", ephemeral=True)

    class ScissorsButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="✌️", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id in game_states[interaction.message.id]:
                game_states[interaction.message.id][interaction.user.id] = "scissors"
                embed = get_winner(interaction)
                if embed is not None:
                    await interaction.response.edit_message(embed=embed, view=None)
                    game_states.pop(interaction.message.id)
                else:
                    await interaction.response.send_message("你出了剪刀！", ephemeral=True)
            else:
                await interaction.response.send_message("你不是這場遊戲的玩家！", ephemeral=True)

    async def on_timeout(self):
        try:
            game_states.pop(self.message.id)
            await self.message.edit(view=None)
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
            await self.message.edit(view=None)
        except discord.NotFound:
            pass

class PveView(discord.ui.View):
    def __init__(self, author: discord.User):
        super().__init__()
        self.author = author
        self.message = None
        self.add_item(self.StartButton())
        self.add_item(self.CancelButton())

    class StartButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="開始", style=discord.ButtonStyle.primary)

        async def callback(self, interaction: discord.Interaction):
            if interaction.user == self.view.author:
                view = GameView()
                embed = LobbyEmbed(self.view.author.id, -1, "遊戲進行中")
                state = {self.view.author.id: None, -1: None}
                choices = ["rock", "paper", "scissors"]
                state = {interaction.user.id: None, -1: random.choice(choices)}
                game_states[interaction.message.id] = state
                await interaction.response.edit_message(embed=embed, view=view)
                view.message = await interaction.original_response()
            else:
                await interaction.response.send_message(
                    "請自行使用 ``/rps`` 指令遊玩！", ephemeral=True
                )

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
            await self.message.edit(view=None)
        except discord.NotFound:
            pass


# class ChooseOpponentView(discord.ui.View):
#     def __init__(self):
#         super().__init__()
#         self.message = None
#         self.add_item(self.PvpButton())
#         self.add_item(self.PvEButton())

#     class PvpButton(discord.ui.Button):
#         def __init__(self):
#             super().__init__(label="其他老師", style=discord.ButtonStyle.primary)

#         async def callback(self, interaction: discord.Interaction):
#             view = FindOpponentView(interaction.user)
#             embed = LobbyEmbed(interaction.user.id, None, "等待對手中...")
#             await interaction.response.send_message(view=view, embed=embed)
#             view.message = await interaction.original_response()
#             await interaction.followup.delete_message(interaction.message.id)

#     class PvEButton(discord.ui.Button):
#         def __init__(self):
#             super().__init__(label="彩奈", style=discord.ButtonStyle.primary)

#         async def callback(self, interaction: discord.Interaction):
#             view = GameView()
#             embed = LobbyEmbed(interaction.user.id, -1, "遊戲進行中")
#             choices = ["rock", "paper", "scissors"]
#             state = {interaction.user.id: None, -1: random.choice(choices)}
#             await interaction.response.send_message(embed=embed, view=view)
#             view.message = await interaction.original_response()
#             game_states[view.message.id] = state
#             await interaction.followup.delete_message(interaction.message.id)

#     async def on_timeout(self):
#         try:
#             for item in self.children:
#                 item.disabled = True
#             await self.message.edit(view=self)
#         except discord.NotFound:
#             pass


class Rps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="rps", description="來猜拳吧！")
    @app_commands.describe(opponent="選擇對手")
    @app_commands.choices(opponent=[
        app_commands.Choice(name="其他老師", value="pvp"),
        app_commands.Choice(name="彩奈", value="pve")
    ])
    async def rps(self, interaction: discord.Interaction, opponent: str):
        if opponent == "pvp":
            view = FindOpponentView(interaction.user)
            embed = LobbyEmbed(interaction.user.id, None, "等待對手中...")
            await interaction.response.send_message(embed=embed, view=view)
            view.message = await interaction.original_response()
        elif opponent == "pve":
            view = PveView(interaction.user)
            embed = discord.Embed(title="來跟彩奈玩吧！", color=discord.Color.green())
            await interaction.response.send_message(embed=embed, view=view)
            view.message = await interaction.original_response()

async def setup(bot: commands.Bot):
    await bot.add_cog(Rps(bot))
