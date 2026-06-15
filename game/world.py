from .dungeon import generate
from .entities import Player


class World:
    def __init__(self):
        self.tiles, self.rooms, self.spawn = generate()
        self.players  = {}    # id -> Player
        self.messages = []
        self.tick_num = 0

    def add_player(self, player):
        player.x, player.y = self.spawn
        self.players[player.id] = player
        self.log(f"{player.name} ({player.cls}) has joined the office.")

    def remove_player(self, pid):
        p = self.players.pop(pid, None)
        if p:
            self.log(f"{p.name} has clocked out.")

    def move_player(self, pid, dx, dy):
        p = self.players.get(pid)
        if p and p.alive:
            p.move(dx, dy, self.tiles)

    def tick(self):
        self.tick_num += 1
        # Future: enemy AI, hazard ticks, status effects

    def log(self, msg):
        self.messages.append(msg)
        if len(self.messages) > 100:
            self.messages = self.messages[-100:]

    def viewport(self, cx, cy, vw, vh):
        """Slice of the tile map centred on (cx, cy)."""
        h = len(self.tiles)
        w = len(self.tiles[0]) if self.tiles else 0
        x0 = max(0, min(cx - vw // 2, w - vw))
        y0 = max(0, min(cy - vh // 2, h - vh))
        return x0, y0, [row[x0:x0 + vw] for row in self.tiles[y0:y0 + vh]]

    def state_for(self, pid, vw=98, vh=36):
        """Serialisable snapshot sent to one client."""
        p = self.players.get(pid)
        if not p:
            return {}
        x0, y0, view = self.viewport(p.x, p.y, vw, vh)
        return {
            "type":     "state",
            "view":     ["".join(row) for row in view],
            "view_x":   x0,
            "view_y":   y0,
            "players":  [pl.to_dict() for pl in self.players.values()],
            "messages": self.messages[-MSG_H:],
            "tick":     self.tick_num,
        }


# Import here to avoid circular at module level
from .config import MSG_H
