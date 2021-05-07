import pickle

item_data = (("Gorgeous T-Shirt", 75, 30), ("Amazing Shorts", 69, 19),
             ("Cute Crop Top", 55, 14), ("Snazzy Jacket", 169, 22),
             ("Stylish Pants", 110, 8), ("Colourful Bucket Hat", 39, 5),
             ("Archaic Gloves", 109, 2), ("Cosy Scarf", 39, 6),
             ("Sturdy Boots", 230, 9), ("Decorated Pyjamas", 89, 12),
             ("Flamboyant Socks", 22, 18), ("Handsome Tuxedo", 699, 2),
             ("Pretty Skirt", 65, 14), ("Fancy Belt", 99, 5))

with open('item_data', 'wb') as f:
    pickle.dump(item_data, f)
