# Helper file to remove unwanted skins from the skins list
import json
import os.path

#TODO : Remove cheap skins

def is_valid(skin_name: str) -> bool:
    if (
            skin_name.startswith('Sticker') or
            'Graffiti' in skin_name or
            skin_name.startswith('Music Kit') or
            'Souvenir' in skin_name or
            'Case' in skin_name or
            '★' in skin_name or
            'Knife' in skin_name or
            'Gloves' in skin_name or
            'Agent' in skin_name or
            'Patch' in skin_name or
            'Capsule' in skin_name or
            'Well-Worn' in skin_name or
            'Battle-Scarred' in skin_name or
            'StatTrak™' in skin_name or
            'Charm' in skin_name or
            'Gift Package' in skin_name or
            'Pin' in skin_name or
            'Viewer Pass' in skin_name or
            'Music Kit' in skin_name or
            'Pass' in skin_name or
            'Legends' in skin_name or
            'Challengers' in skin_name or
            'CZ75-Auto' in skin_name or
            'Dual Berettas' in skin_name or
            'P2000' in skin_name or
            'R8 Revolver' in skin_name or
            'Five-SeveN' in skin_name or
            'Nova' in skin_name or
            'Sawed-Off' in skin_name or
            'MAG-7' in skin_name or
            'XM1014' in skin_name or
            'M249' in skin_name or
            'Negev' in skin_name or
            'MAC-10' in skin_name or
            'MP5-SD' in skin_name or
            'MP7' in skin_name or
            'MP9' in skin_name or
            'PP-Bizon' in skin_name or
            'P90' in skin_name or
            'UMP-45' in skin_name or
            'G3SG1' in skin_name or
            'AUG' in skin_name or
            'Galil AR' in skin_name or
            'FAMAS' in skin_name or
            'SG 553' in skin_name or
            'SCAR-20' in skin_name or
            'SSG 08' in skin_name or
            'Zeus x27' in skin_name or
            'Tec-9' in skin_name or
            'P250' in skin_name
            or not '(' in skin_name
    ):
        return False

    return True

with open('../data/marketplaceids.json', 'r', encoding="utf8") as f:
    names = json.load(f)

initItems = len(names['items'].keys())

unvalid_skins = {}

if os.path.isfile("../data/wrong.txt"):
    with open("../data/wrong.txt", 'r', encoding='utf-8') as file:
        for line in file:
            unvalid_skins[line.strip()] = True

for name in list(names['items'].keys()):
    if not is_valid(name) or name in unvalid_skins:
        names['items'].pop(name)

with open('../data/marketplaceids.json', 'w', encoding="utf8") as f:
    json.dump(names, f, indent=4)


print("Removed " + str(initItems - len(names['items'].keys())) + " skins from the list")
