#!/usr/bin/env python3
"""
office-terminal — curses client
Handles keyboard input and renders state received from the server.
"""

import curses
import json
import socket
import sys
import threading

from game.config import HOST, PORT, MAP_W, MAP_H, PANEL_W, MSG_H
from game.sprite import draw_sprite

# ── Key bindings ───────────────────────────────────────────────────────────────
INPUT_KEYS = {
    curses.KEY_UP:    'w',  curses.KEY_DOWN:  's',
    curses.KEY_LEFT:  'a',  curses.KEY_RIGHT: 'd',
    ord('w'): 'w',  ord('a'): 'a',
    ord('s'): 's',  ord('d'): 'd',
    ord('k'): 'k',  ord('h'): 'h',
    ord('j'): 'j',  ord('l'): 'l',
}

# ── Tile rendering ─────────────────────────────────────────────────────────────
#  (color_pair_index, bold, dim)
TILE_STYLE = {
    '#': (1, False, True),    # wall       — white dim
    '.': (2, False, True),    # floor      — dark
    '+': (3, True,  False),   # door       — yellow bold
    '$': (4, True,  False),   # chest      — yellow bold
    '>': (5, True,  False),   # stairs     — cyan bold
}

class GameClient:
    def __init__(self, host, port):
        self.host    = host
        self.port    = port
        self.sock    = None
        self.state   = {}
        self.lock    = threading.Lock()
        self.running = True

    # ── Network ───────────────────────────────────────────────────────────────

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.sock.settimeout(5)

    def send(self, msg: dict):
        try:
            self.sock.sendall((json.dumps(msg) + "\n").encode())
        except Exception:
            self.running = False

    def recv_loop(self):
        buf = ""
        while self.running:
            try:
                chunk = self.sock.recv(8192).decode(errors="replace")
                if not chunk:
                    self.running = False
                    break
                buf += chunk
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    try:
                        with self.lock:
                            self.state = json.loads(line)
                    except json.JSONDecodeError:
                        pass
            except socket.timeout:
                continue
            except Exception:
                self.running = False

    # ── Curses entry point ────────────────────────────────────────────────────

    def run(self, stdscr):
        curses.start_color()
        curses.use_default_colors()
        curses.curs_set(0)
        stdscr.nodelay(True)

        curses.init_pair(1, curses.COLOR_WHITE,   -1)   # wall
        curses.init_pair(2, curses.COLOR_BLACK,   -1)   # floor
        curses.init_pair(3, curses.COLOR_YELLOW,  -1)   # door
        curses.init_pair(4, curses.COLOR_YELLOW,  -1)   # chest
        curses.init_pair(5, curses.COLOR_CYAN,    -1)   # stairs
        curses.init_pair(6, curses.COLOR_WHITE,   -1)   # player
        curses.init_pair(7, curses.COLOR_GREEN,   -1)   # HP bar
        curses.init_pair(8, curses.COLOR_RED,     -1)   # danger / low HP

        recv_thread = threading.Thread(target=self.recv_loop, daemon=True)
        recv_thread.start()

        while self.running:
            key = stdscr.getch()

            if key == ord('q'):
                self.running = False
                break

            if key in INPUT_KEYS:
                self.send({"type": "input", "key": INPUT_KEYS[key]})

            with self.lock:
                state = dict(self.state)

            self._draw(stdscr, state)
            curses.napms(40)   # ~25 fps render ceiling

    # ── Drawing ───────────────────────────────────────────────────────────────

    def _draw(self, stdscr, state):
        stdscr.erase()
        scr_h, scr_w = stdscr.getmaxyx()

        # ── Size warning ──────────────────────────────────────────────────
        from game.config import TERM_W, TERM_H
        if scr_w < TERM_W or scr_h < TERM_H:
            msg = f"Terminal too small: {scr_w}×{scr_h} (need {TERM_W}×{TERM_H})"
            try:
                stdscr.addstr(0, 0, msg, curses.A_BOLD)
            except curses.error:
                pass
            stdscr.refresh()
            return

        # ── Header bar ────────────────────────────────────────────────────
        tick   = state.get("tick", 0)
        header = f"  OFFICE TERMINAL  │  tick {tick}  │  q=quit  wasd/hjkl=move  "
        try:
            stdscr.addstr(0, 0, header.ljust(scr_w - 1), curses.A_REVERSE)
        except curses.error:
            pass

        if not state:
            try:
                stdscr.addstr(2, 2, "Connecting to server…")
            except curses.error:
                pass
            stdscr.refresh()
            return

        # ── Map tiles ─────────────────────────────────────────────────────
        view = state.get("view", [])
        vx   = state.get("view_x", 0)
        vy   = state.get("view_y", 0)

        for row_i, row in enumerate(view):
            sy = row_i + 1
            if sy > MAP_H:
                break
            for col_i, ch in enumerate(row):
                sx = col_i + 1
                if sx >= MAP_W:
                    break
                pair, bold, dim = TILE_STYLE.get(ch, (1, False, False))
                attr = curses.color_pair(pair)
                if bold: attr |= curses.A_BOLD
                if dim:  attr |= curses.A_DIM
                try:
                    stdscr.addch(sy, sx, ch, attr)
                except curses.error:
                    pass

        # ── Player sprites overlaid on map ────────────────────────────────
        # Sprite is 8 cols × 4 rows; center it on the player's tile.
        # Draw order: tiles first, sprites on top, border+panel last
        # (so any sprite bleed past MAP_W gets overwritten by the panel).
        for p in state.get("players", []):
            wx, wy  = p["x"], p["y"]
            sx = (wx - vx) + 1   # screen col of the player's tile
            sy = (wy - vy) + 1   # screen row of the player's tile
            draw_sprite(
                stdscr,
                sy - 2,           # center sprite vertically on tile (4 rows → offset -2)
                sx - 4,           # center sprite horizontally on tile (8 cols → offset -4)
                tuple(p.get("hair",    [80,  48,  12])),
                tuple(p.get("skin",    [238, 195, 145])),
                tuple(p.get("clothes", [28,  72,  165])),
                p.get("facing", "right"),
            )

        # ── Vertical border ───────────────────────────────────────────────
        border_x = MAP_W
        for y in range(0, MAP_H + 2):
            try:
                stdscr.addch(y, border_x, '│')
            except curses.error:
                pass

        # ── Side panel ────────────────────────────────────────────────────
        px = MAP_W + 2          # panel left edge (col 102)
        py = 1
        SPRITE_W = 8            # sprite occupies 8 cols × 4 rows
        INFO_X   = px + SPRITE_W + 2   # text starts 2 cols after sprite

        try:
            stdscr.addstr(py, px, "[ OFFICE TERMINAL ]", curses.A_BOLD)
            py += 1
            stdscr.addstr(py, px, "─" * (PANEL_W - 2))
            py += 2
        except curses.error:
            pass

        for p in state.get("players", []):
            if py + 4 >= MAP_H:   # stop if we'd overflow the panel
                break

            hp      = p.get("hp", 0)
            max_hp  = p.get("max_hp", 1)
            bar_w   = PANEL_W - SPRITE_W - 10
            filled  = max(0, int(bar_w * hp / max_hp))
            bar     = "█" * filled + "░" * (bar_w - filled)
            hp_pair = 8 if hp / max_hp < 0.3 else 7
            cls     = p.get("cls", "warrior")
            name    = p.get("name", "?")[:PANEL_W - SPRITE_W - 4]
            facing  = p.get("facing", "right")
            hair    = tuple(p.get("hair",    [80,  48,  12]))
            skin    = tuple(p.get("skin",    [238, 195, 145]))
            clothes = tuple(p.get("clothes", [28,  72,  165]))

            # Sprite on the left (8 cols × 4 rows)
            draw_sprite(stdscr, py, px, hair, skin, clothes, facing)

            # Info to the right of the sprite
            try:
                stdscr.addstr(py,     INFO_X, name,  curses.A_BOLD)
                stdscr.addstr(py + 1, INFO_X, cls)
                stdscr.addstr(py + 2, INFO_X, f"HP [{bar}]",
                              curses.color_pair(hp_pair))
                stdscr.addstr(py + 3, INFO_X, f"   {hp}/{max_hp}")
            except curses.error:
                pass

            py += 6   # 4 sprite rows + 1 blank gap + 1 header row above

        # ── Horizontal separator ──────────────────────────────────────────
        sep_y = MAP_H + 1
        try:
            stdscr.addstr(sep_y, 0, "─" * (scr_w - 1))
        except curses.error:
            pass

        # ── Message log ───────────────────────────────────────────────────
        for i, msg in enumerate(state.get("messages", [])[-MSG_H:]):
            try:
                stdscr.addstr(sep_y + 1 + i, 2, msg[:scr_w - 4])
            except curses.error:
                pass

        stdscr.refresh()


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    host = sys.argv[1] if len(sys.argv) > 1 else HOST
    client = GameClient(host, PORT)
    try:
        client.connect()
    except ConnectionRefusedError:
        print(f"Cannot connect to {host}:{PORT} — start the server first.")
        sys.exit(1)

    curses.wrapper(client.run)


if __name__ == "__main__":
    main()
