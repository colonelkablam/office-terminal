import uuid
from .config import WALL, CLASS_HAIR, CLASS_SKIN, CLASS_CLOTHES

CLASSES = {
    "warrior": {"label": "Project Manager", "hp": 30, "atk": 5,  "char": "@"},
    "mage":    {"label": "Developer",        "hp": 20, "atk": 8,  "char": "@"},
    "cleric":  {"label": "Office Clerk",     "hp": 25, "atk": 4,  "char": "@"},
}


class Player:
    def __init__(self, cls="warrior", name="Employee"):
        self.id     = str(uuid.uuid4())[:8]
        self.cls    = cls
        self.name   = name
        self.x      = 0
        self.y      = 0
        stats       = CLASSES.get(cls, CLASSES["warrior"])
        self.max_hp = stats["hp"]
        self.hp     = stats["hp"]
        self.atk    = stats["atk"]
        self.alive   = True
        self.facing  = "right"
        self.hair    = CLASS_HAIR.get(cls,    (80, 48, 12))
        self.skin    = CLASS_SKIN.get(cls,    (238, 195, 145))
        self.clothes = CLASS_CLOTHES.get(cls, (28, 72, 165))

    def move(self, dx, dy, tiles):
        nx, ny = self.x + dx, self.y + dy
        if 0 <= ny < len(tiles) and 0 <= nx < len(tiles[0]):
            if tiles[ny][nx] != WALL:
                self.x, self.y = nx, ny
                self.facing = "right" if dx > 0 else ("left" if dx < 0 else self.facing)
                return True
        return False

    def to_dict(self):
        return {
            "id":     self.id,
            "cls":    self.cls,
            "name":   self.name,
            "x":      self.x,
            "y":      self.y,
            "hp":     self.hp,
            "max_hp": self.max_hp,
            "facing":  self.facing,
            "hair":    list(self.hair),
            "skin":    list(self.skin),
            "clothes": list(self.clothes),
        }
