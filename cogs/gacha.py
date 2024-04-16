from discord.ext import commands
import discord
import json
import random
from discord import app_commands
from pathlib import Path
import PIL
import PIL.Image
import PIL.ImageChops
import math

pwd = Path(__file__).parent

r = []
sr = []
ssr = []
limited_ssr = []
fes_ssr = []
current_banners = []

jp_r = []
jp_sr = []
jp_ssr = []
jp_limited_ssr = []
jp_fes_ssr = []
jp_current_banners = []

with open((pwd/"../gacha_data/global/r.txt").as_posix(), "r") as f:
    r = f.read().splitlines()
with open((pwd/"../gacha_data/global/sr.txt").as_posix(), "r") as f:
    sr = f.read().splitlines()
with open((pwd/"../gacha_data/global/ssr.txt").as_posix(), "r") as f:
    ssr = f.read().splitlines()
with open((pwd/"../gacha_data/global/limited_ssr.txt").as_posix(), "r") as f:
    limited_ssr = f.read().splitlines()
with open((pwd/"../gacha_data/global/fes_ssr.txt").as_posix(), "r") as f:
    fes_ssr = f.read().splitlines()
with open((pwd/"../gacha_data/global/current_banners.json").as_posix(), "r") as f:
    current_banners = json.load(f)

with open((pwd/"../gacha_data/japan/r.txt").as_posix(), "r", encoding="utf-8") as f:
    jp_r = f.read().splitlines()
with open((pwd/"../gacha_data/japan/sr.txt").as_posix(), "r", encoding="utf-8") as f:
    jp_sr = f.read().splitlines()
with open((pwd/"../gacha_data/japan/ssr.txt").as_posix(), "r", encoding="utf-8") as f:
    jp_ssr = f.read().splitlines()
with open((pwd/"../gacha_data/japan/limited_ssr.txt").as_posix(), "r", encoding="utf-8") as f:
    jp_limited_ssr = f.read().splitlines()
with open((pwd/"../gacha_data/japan/fes_ssr.txt").as_posix(), "r", encoding="utf-8") as f:
    jp_fes_ssr = f.read().splitlines()
with open((pwd/"../gacha_data/japan/current_banners.json").as_posix(), "r", encoding="utf-8") as f:
    jp_current_banners = json.load(f)
with open((pwd/"../gacha_data/japan/translate.json").as_posix(), "r", encoding="utf-8") as f:
    translate = json.load(f)

mask = PIL.Image.open((pwd/"../assets/mask.png").as_posix())
border = PIL.Image.open((pwd/"../assets/border.png").as_posix())
star = PIL.Image.open((pwd/"../assets/star.png").as_posix())
two_star = PIL.Image.open((pwd/"../assets/two_star.png").as_posix())
three_star = PIL.Image.open((pwd/"../assets/three_star.png").as_posix())
purple_glow = PIL.Image.open((pwd/"../assets/purple_glow.png").as_posix())
yellow_glow = PIL.Image.open((pwd/"../assets/yellow_glow.png").as_posix())
pickup = PIL.Image.open((pwd/"../assets/pickup.png").as_posix())

def pull(choice, spark):
    server = "gl" if choice < len(current_banners) else "jp"
    server = "jp" if choice == -2 else server
    
    new_r = (r if server == "gl" else jp_r).copy()
    new_sr = (sr if server == "gl" else jp_sr).copy()
    new_ssr = (ssr if server == "gl" else jp_ssr).copy()
    new_limited_ssr = (limited_ssr if server == "gl" else jp_limited_ssr).copy()
    new_fes_ssr = (fes_ssr if server == "gl" else jp_fes_ssr).copy()
    banner = current_banners if server == "gl" else jp_current_banners

    pickup_sr = []
    pickup_ssr = []

    # R, SR, SSR, Pickup SR, Pickup SSR, Fes SSR
    weight = [78.5, 18.5, 3, 0, 0, 0]
    if choice > -1:
        if server == "jp":
            choice -= len(current_banners)
        if banner[choice]["gachaType"] == "PickupGacha":
            for rateup in banner[choice]["rateups"]:
                if rateup["raity"] == "SR":
                    new_sr.remove(rateup["name"])
                    # Move SR to Pickup SR
                    weight[1] -= 3
                    weight[3] += 3
                    pickup_sr.append(rateup["name"])
                else:
                    new_ssr.remove(rateup["name"])
                    # Move SSR to Pickup SSR
                    weight[2] -= 0.7
                    weight[4] += 0.7
                    pickup_ssr.append(rateup["name"])
        elif banner[choice]["gachaType"] == "LimitedGacha":
            for rateup in banner[choice]["rateups"]:
                new_limited_ssr.remove(rateup["name"])
                # Move SSR to Pickup SSR
                weight[2] -= 0.7
                weight[4] += 0.7
                pickup_ssr.append(rateup["name"])
        elif banner[choice]["gachaType"] == "FesGacha":
            # Fes SSR rate is 6%, Fes SSR rate is 9%, Pickup SSR rate is 0.7%
            weight = [75.5, 18.5, 4.4, 0, 0.7, 0.9]
            for rateup in banner[choice]["rateups"]:
                new_fes_ssr.remove(rateup["name"])
                pickup_ssr.append(rateup["name"])
    if spark:
        weight[1] += weight[0]
        weight[0] = 0
    print(f"Pickup SSR: {pickup_ssr}")
    print(f"Pickup SR: {pickup_sr}")
    print(f"Weight: {weight}")
    print(f"Spark: {spark}")
    print("")

    raity_result = random.choices(["R", "SR", "SSR", "Pickup SR", "Pickup SSR", "Fes SSR"], weight)[0]
    if raity_result == "R":
        return random.choice(new_r), raity_result, server
    elif raity_result == "SR":
        return random.choice(new_sr), raity_result, server
    elif raity_result == "SSR":
        return random.choice(new_ssr), raity_result, server
    elif raity_result == "Pickup SR":
        return random.choice(pickup_sr), raity_result, server
    elif raity_result == "Pickup SSR":
        return random.choice(pickup_ssr), raity_result, server
    elif raity_result == "Fes SSR":
        return random.choice(new_fes_ssr), raity_result, server
    
def pull_ten(choice):
    results = []
    for i in range(10):
        result = {}
        result["name"], result["raity"], result["server"] = pull(choice, False if i != 9 else True)
        results.append(result)
    return results

def generate_image(char_images):
    image_count = len(char_images)

    if image_count > 1:
        base_image = PIL.Image.new("RGBA", size=(640, 140*math.ceil(image_count/5)+20), color=(194, 229, 245, 255))
        for i in range(len(char_images)):
            base_image.alpha_composite(char_images[i], dest=(i%5*120, i//5*140))
    else: 
        base_image = PIL.Image.new("RGBA", size=(640, 300), color=(194, 229, 245, 255))
        base_image.alpha_composite(char_images[0], dest=(240, 70))
    base_image.save("result.png")

def create_image_single(result):
    server = result["server"]
    base_char_image = PIL.Image.new("RGBA", size=(160, 160), color=(0, 0, 0, 0))
    if server == "gl":
        char = PIL.Image.open((pwd/f"../gacha_data/global/image/{result['name']}.png").as_posix())
    else:
        char = PIL.Image.open((pwd/f"../gacha_data/japan/image/{translate[result['name']]}.png").as_posix())
    char = char.convert("RGBA")
    print(PIL.ImageChops.difference(char, mask))
    char = PIL.ImageChops.multiply(char, mask)
    base_char_image.alpha_composite(char, dest=(20, 20))
    base_char_image.save("result2.png")
    raity = result["raity"]
    if raity == "R":
        base_char_image.alpha_composite(border, dest=(0, 0))
        base_char_image.alpha_composite(star, dest=(0, 0))
    elif raity == "SR" or raity == "Pickup SR":
        base_char_image.alpha_composite(yellow_glow, dest=(0, 0))
        base_char_image.alpha_composite(border, dest=(0, 0))
        base_char_image.alpha_composite(two_star, dest=(0, 0))
        if raity == "Pickup SR":
            base_char_image.alpha_composite(pickup, dest=(0, 0))
    elif raity == "SSR" or raity == "Pickup SSR":
        base_char_image.alpha_composite(purple_glow, dest=(0, 0))
        base_char_image.alpha_composite(border, dest=(0, 0))
        base_char_image.alpha_composite(three_star, dest=(0, 0))
        if raity == "Pickup SSR":
            base_char_image.alpha_composite(pickup, dest=(0, 0))
    return base_char_image

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = []
        for banner in current_banners:
            banner_name = ''
            banner_type = banner["gachaType"]
            if banner_type == "PickupGacha":
                banner_type = "特選招募"
            elif banner_type == "LimitedGacha":
                banner_type = "限定招募"
            elif banner_type == "FesGacha":
                banner_type = "Fes招募"
            for rateup in banner["rateups"]:
                banner_name += rateup["name"]
                if rateup != banner["rateups"][-1]:
                    banner_name += " & "
            options.append(discord.SelectOption(label=f"國際服：{banner_name}", value=str(current_banners.index(banner)), description=banner_type))
        options.append(discord.SelectOption(label="國際服：常駐招募", value="-1", description=""))

        for banner in jp_current_banners:
            banner_name = ''
            banner_type = banner["gachaType"]
            if banner_type == "PickupGacha":
                banner_type = "特選招募"
            elif banner_type == "LimitedGacha":
                banner_type = "限定招募"
            elif banner_type == "FesGacha":
                banner_type = "Fes招募"
            for rateup in banner["rateups"]:
                banner_name += rateup["name"]
                if rateup != banner["rateups"][-1]:
                    banner_name += " & "
            options.append(discord.SelectOption(label=f"日服：{banner_name}", value=str(jp_current_banners.index(banner) + len(current_banners)), description=banner_type))
        options.append(discord.SelectOption(label="日服：常駐招募", value="-2", description=""))

        super().__init__(placeholder="選擇卡池", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        choice = int(self.values[0])
        results = pull_ten(choice)
        embed = discord.Embed(title="招募結果", color=discord.Color.blue())
        char_images = []
        
        for i in results:
            char_images.append(create_image_single(i))
        generate_image(char_images)
        file = discord.File("result.png")
        embed.set_image(url="attachment://result.png")

        await interaction.followup.send(content=interaction.user.mention, file=file, embed=embed, view=self.view)

class View(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())

class Gacha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="gacha", description="Gacha commands")
    async def gacha(self, interaction: discord.Interaction):
        embed = discord.Embed(title="招募", description="選擇你的招募", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, view=View(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(Gacha(bot))
    print("Gacha cog loaded")