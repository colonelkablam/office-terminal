import random
from .config import WALL, FLOOR, CHEST, STAIR, DUNGEON_W, DUNGEON_H


class Room:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h

    @property
    def cx(self): return self.x + self.w // 2

    @property
    def cy(self): return self.y + self.h // 2

    def inner(self):
        for ry in range(self.y + 1, self.y + self.h - 1):
            for rx in range(self.x + 1, self.x + self.w - 1):
                yield rx, ry

    def overlaps(self, other, pad=2):
        return (self.x - pad < other.x + other.w and
                self.x + self.w + pad > other.x and
                self.y - pad < other.y + other.h and
                self.y + self.h + pad > other.y)


def _hcorridor(tiles, x1, x2, y):
    for x in range(min(x1, x2), max(x1, x2) + 1):
        tiles[y][x] = FLOOR


def _vcorridor(tiles, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        tiles[y][x] = FLOOR


def generate(width=DUNGEON_W, height=DUNGEON_H, max_rooms=28, seed=None):
    if seed is not None:
        random.seed(seed)

    tiles = [[WALL] * width for _ in range(height)]
    rooms = []

    for _ in range(max_rooms * 8):
        if len(rooms) >= max_rooms:
            break
        w = random.randint(6, 18)
        h = random.randint(5, 12)
        x = random.randint(1, width - w - 2)
        y = random.randint(1, height - h - 2)
        room = Room(x, y, w, h)

        if any(room.overlaps(r) for r in rooms):
            continue

        for rx, ry in room.inner():
            tiles[ry][rx] = FLOOR

        if rooms:
            prev = rooms[-1]
            if random.random() < 0.5:
                _hcorridor(tiles, prev.cx, room.cx, prev.cy)
                _vcorridor(tiles, prev.cy, room.cy, room.cx)
            else:
                _vcorridor(tiles, prev.cy, room.cy, prev.cx)
                _hcorridor(tiles, prev.cx, room.cx, room.cy)

        rooms.append(room)

    # Scatter chests in some rooms (not the first)
    for room in rooms[2:]:
        if random.random() < 0.25:
            tiles[room.cy][room.cx] = CHEST

    # Stairs down in the last room
    if rooms:
        last = rooms[-1]
        tiles[last.cy][last.cx] = STAIR

    spawn = (rooms[0].cx, rooms[0].cy) if rooms else (2, 2)
    return tiles, rooms, spawn
