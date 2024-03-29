import json
import random

r = []
sr = []
ssr = []
current_banner = []

raity = ['R','SR','SSR','SRP','SSRP']
icon = ['🟦','🟨','🟪','🟨','🟪']
weight = [78.5, 18.5, 3.0, 0.0, 0.0]

with open("./gacha_data/global/r.txt", "r") as f:
    for line in f:
        r.append(line.strip())
with open("./gacha_data/global/sr.txt", "r") as f:
    for line in f:
        sr.append(line.strip())
with open("./gacha_data/global/ssr.txt", "r") as f:
    for line in f:
        ssr.append(line.strip())
with open("./gacha_data/global/rateups.json", "r") as f:
    current_banner = json.load(f)

def Pull(banner, spark):
    # return random.choices(raity, weights=weight, k=1)[0]
    for rateup in current_banner[banner]:
        if rateup in sr:
            sr.remove(rateup)
            weight[1] = 15.5
            weight[4] = 3.0
        if rateup in ssr:
            ssr.remove(rateup)
            weight[2] = 2.3
            weight[4] = 0.7
    if spark:
        weight[1] += weight[0]
        weight[0] = 0.0
    print(weight)
    raity_result = random.choices(raity, weights=weight, k=1)
    if raity_result[0] == raity[0]:
        return random.choices(r, k=1)[0], raity_result[0]
    elif raity_result[0] == raity[1]:
        return random.choices(sr, k=1)[0], raity_result[0]
    elif raity_result[0] == raity[2]:
        return random.choices(ssr, k=1)[0], raity_result[0]
    elif raity_result[0] == raity[3]:
        key_list = list(current_banner[banner].keys())
        val_list = list(current_banner[banner].values())
        position = val_list.index(2)
        return key_list[position], raity_result[0]
    elif raity_result[0] == raity[4]:
        key_list = list(current_banner[banner].keys())
        val_list = list(current_banner[banner].values())
        position = val_list.index(3)
        return key_list[position], raity_result[0]
            
def PullTen(banner):
    ten_result = []
    for i in range(10):
        result = {}
        if i == 9:
            spark = True
            for j in ten_result:
                if list(j.values())[0] == raity[1] or list(j.values())[0] == raity[2] or list(j.values())[0] == raity[3] or list(j.values())[0] == raity[4]:
                    spark = False
                    break
            name_result, raity_result = Pull(banner, spark)
        else:
            name_result, raity_result = Pull(banner, False)
        result[name_result] = raity_result
        ten_result.append(result)
    return ten_result

def PullTenIcon(result):
    output = ''

    for i in range(10):
        if i == 5:
            output += '\n'
        if result[i] == raity[0]:
            output += icon[0]
        elif result[i] == raity[1]:
            output += icon[1]
        elif result[i] == raity[2]:
            output += icon[2]
    
    return output