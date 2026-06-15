# Terminal layout (132×43)
TERM_W  = 132
TERM_H  = 43

MAP_W   = 100   # viewport columns (cols 0-99)
MAP_H   = 38    # viewport rows    (rows 1-38, row 0 = header)
PANEL_W = 30    # side panel       (cols 101-131, col 100 = border)
MSG_H   = 3     # message rows     (rows 40-42, row 39 = separator)

# Dungeon (larger than viewport — scrolls)
DUNGEON_W = 200
DUNGEON_H = 80

# Network
HOST      = "127.0.0.1"
PORT      = 9876
TICK_RATE = 15   # ticks per second

# Class colours (hair, skin, clothes) used for sprites and UI
CLASS_CLOTHES = {
    "warrior": (28,  72, 165),   # corporate navy
    "mage":    (60,  30, 130),   # hoodie purple
    "cleric":  (140, 120, 80),   # beige / khaki
}
CLASS_HAIR = {
    "warrior": (80,  48,  12),
    "mage":    (22,  22,  22),
    "cleric":  (185, 148, 60),
}
CLASS_SKIN = {
    "warrior": (238, 195, 145),
    "mage":    (200, 158, 118),
    "cleric":  (252, 218, 178),
}

# Tile characters
WALL  = '#'
FLOOR = '.'
DOOR  = '+'
CHEST = '$'
STAIR = '>'
