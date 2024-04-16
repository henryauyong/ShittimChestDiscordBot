import PIL 
import PIL.Image
import PIL.ImageChops

mask = PIL.Image.open("./assets/mask.png")
char = PIL.Image.open("./gacha_data/global/image/Aru.png")
border = PIL.Image.open("./assets/border.png")
star = PIL.Image.open("./assets/star.png")
two_star = PIL.Image.open("./assets/two_star.png")
three_star = PIL.Image.open("./assets/three_star.png")

base = PIL.Image.new("RGBA", size=(600, 240), color=(0, 0, 0, 0))

char = PIL.ImageChops.multiply(char, mask)
char.alpha_composite(border)
char.alpha_composite(three_star)
base.alpha_composite(char, (0, 0))

base.show()