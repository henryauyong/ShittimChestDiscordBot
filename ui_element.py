import discord
from discord import ui
import gacha

# class AddRoleUi(ui.Modal, title="Add Role"):
#     name = ui.TextInput(label="Role Name", placeholder="Role Name")
    
#     async def on_submit(self, interaction:discord.Interaction):
#         guild = interaction.guild
#         role = discord.utils.get(guild.roles, name=self.name.value)
#         if role is None:
#             role = await guild.create_role(name=self.name.value)
#             await interaction.response.send_message("Role Added", ephemeral=True)
#         else:
#             await interaction.response.send_message("Role Already Exists", ephemeral=True)
#         await interaction.user.add_roles(role)

# class ToAddRoleUiButton(discord.ui.Button):
#     def __init__(self):
#         super().__init__(style=discord.ButtonStyle.primary, label="Add Role")

#     async def callback(self, interaction:discord.Interaction):
#         await interaction.response.send_modal(AddRoleUi())

# class MainUiEmbed(discord.Embed):
#     def __init__(self):
#         super().__init__(title="自訂身份組", description="可以自訂身份組", color=discord.Color.green())

# class MainUi(discord.ui.View):
#     def __init__(self):
#         super().__init__()
#         self.add_item(ToAddRoleUiButton())

class GachaButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.primary, label="抽卡")

    async def callback(self, interaction:discord.Interaction):
        result = gacha.PullTen()
        await interaction.response.send_message(gacha.PullTenIcon(result), ephemeral=True)

class MainUi():
    def Embed(self):
        return discord.Embed(title="歡迎來到シッテムの箱", color=discord.Color.green()) 
    def View(self):
        view = discord.ui.View()
        view.add_item(GachaButton())
        return view