from discord.ext import commands
import discord
import json
import random
from discord import app_commands
from pathlib import Path
import PIL
import PIL.Image
import PIL.ImageChops

pwd = Path(__file__).parent

r = []
sr = []
ssr = []
limited_ssr = []
fes_ssr = []
current_banners = []

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

mask = PIL.Image.open((pwd/"../assets/mask.png").as_posix())
border = PIL.Image.open((pwd/"../assets/border.png").as_posix())
star = PIL.Image.open((pwd/"../assets/star.png").as_posix())
two_star = PIL.Image.open((pwd/"../assets/two_star.png").as_posix())
three_star = PIL.Image.open((pwd/"../assets/three_star.png").as_posix())
purple_glow = PIL.Image.open((pwd/"../assets/purple_glow.png").as_posix())
yellow_glow = PIL.Image.open((pwd/"../assets/yellow_glow.png").as_posix())
pickup = PIL.Image.open((pwd/"../assets/pickup.png").as_posix())

def pull(choice, spark):
    new_sr = sr.copy()
    new_ssr = ssr.copy()
    new_limited_ssr = limited_ssr.copy()
    new_fes_ssr = fes_ssr.copy()
    pickup_sr = []
    pickup_ssr = []

    # R, SR, SSR, Pickup SR, Pickup SSR, Fes SSR
    weight = [78.5, 18.5, 3, 0, 0, 0]
    if choice != -1:
        if current_banners[choice]["gachaType"] == "PickupGacha":
            for rateup in current_banners[choice]["rateups"]:
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
        elif current_banners[choice]["gachaType"] == "LimitedGacha":
            for rateup in current_banners[choice]["rateups"]:
                new_limited_ssr.remove(rateup["name"])
                # Move SSR to Pickup SSR
                weight[2] -= 0.7
                weight[4] += 0.7
                pickup_ssr.append(rateup["name"])
        elif current_banners[choice]["gachaType"] == "FesGacha":
            # Fes SSR rate is 6%, Fes SSR rate is 9%, Pickup SSR rate is 0.7%
            weight = [75.5, 18.5, 4.4, 0, 0.7, 0.9]
            for rateup in current_banners[choice]["rateups"]:
                new_fes_ssr.remove(rateup["name"])
                pickup_ssr.append(rateup["name"])
    if spark:
        weight[1] += weight[0]
        weight[0] = 0

    # print(f"Pickup SSR: {pickup_ssr}")
    # print(f"Weight: {weight}")
    # print(f"Spark: {spark}")
    # print("")

    raity_result = random.choices(["R", "SR", "SSR", "Pickup SR", "Pickup SSR", "Fes SSR"], weight)[0]
    if raity_result == "R":
        return random.choice(r), raity_result
    elif raity_result == "SR":
        return random.choice(new_sr), raity_result
    elif raity_result == "SSR":
        return random.choice(new_ssr), raity_result
    elif raity_result == "Pickup SR":
        return random.choice(pickup_sr), raity_result
    elif raity_result == "Pickup SSR":
        return random.choice(pickup_ssr), raity_result
    elif raity_result == "Fes SSR":
        return random.choice(new_fes_ssr), raity_result
    
def pull_ten(choice):
    results = []
    for i in range(10):
        result = {}
        if i == 9:
            result["name"], result["raity"] = pull(choice, True)
            results.append(result) 
        else:
            result["name"], result["raity"] = pull(choice, False)
            results.append(result)
    return results

def create_image(result):
    base_image = PIL.Image.new("RGBA", size=(640, 320), color=(194, 229, 245, 255))
    for i in range(10):
        char_image = PIL.Image.open((pwd/f"../gacha_data/global/image/{result[i]['name']}.png").as_posix())
        char_image = PIL.ImageChops.multiply(char_image, mask)
        if result[i]["raity"] == "R":
            char_image.alpha_composite(border, dest=(-20, -20))
            char_image.alpha_composite(star, dest=(-20, -20))
        elif result[i]["raity"] == "SR" or result[i]["raity"] == "Pickup SR":
            char_image.alpha_composite(yellow_glow, dest=(-20, -20))
            char_image.alpha_composite(border, dest=(-20, -20))
            char_image.alpha_composite(two_star, dest=(-20, -20))
            if result[i]["raity"] == "Pickup SR":
                char_image.alpha_composite(pickup, dest=(-20, -20))
        elif result[i]["raity"] == "SSR" or result[i]["raity"] == "Pickup SSR":
            char_image.alpha_composite(purple_glow, dest=(-20, -20))
            char_image.alpha_composite(border, dest=(-20, -20))
            char_image.alpha_composite(three_star, dest=(-20, -20))
            if result[i]["raity"] == "Pickup SSR":
                char_image.alpha_composite(pickup, dest=(-20, -20))

        if i <= 4:
            base_image.alpha_composite(char_image, (i*120+20, 20))
        else:
            base_image.alpha_composite(char_image, ((i-5)*120+20, 180))
    base_image.save("result.png")

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = []
        for banner in current_banners:
            banner_name = ''
            for rateup in banner["rateups"]:
                banner_name += rateup["name"]
                if rateup != banner["rateups"][-1]:
                    banner_name += " & "
            options.append(discord.SelectOption(label=banner_name, value=str(current_banners.index(banner))))
        options.append(discord.SelectOption(label="常駐招募", value="-1", description="常駐等歪"))
        super().__init__(placeholder="選擇卡池", options=options)

    async def callback(self, interaction: discord.Interaction):
        choice = int(self.values[0])
        results = pull_ten(choice)
        embed = discord.Embed(title="招募結果", color=discord.Color.blue())

        # count = 0
        # while True:
        #     count += 1
        #     if "Ichika" in [i["name"] for i in results]:
        #         break
        #     results = pull_ten(choice)
        # print(f"Pulls: {count*10}")

        # for i in results:
        #     embed.add_field(name=i["name"], value=i["raity"])
        
        create_image(results)
        file = discord.File("result.png")
        embed.set_image(url="attachment://result.png")

        await interaction.response.send_message(content=interaction.user.mention, file=file, embed=embed, view=self.view)

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