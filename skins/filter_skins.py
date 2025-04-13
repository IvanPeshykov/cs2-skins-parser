# Helper file to remove unwanted skins from the skins list
import json

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
            'Capsule' in skin_name
    ):
        return False

    return True

with open('../data/marketplaceids.json', 'r', encoding="utf8") as f:
    names = json.load(f)

initItems = len(names['items'].keys())

for name in list(names['items'].keys()):
    if not is_valid(name):
        names['items'].pop(name)

with open('../data/marketplaceids.json', 'w', encoding="utf8") as f:
    json.dump(names, f, indent=4)

print("Removed " + str(initItems - len(names['items'].keys())) + " skins from the list")
