#!/usr/bin/env python3
"""
office-terminal — game server
Owns all game state. Clients connect, send input, receive state snapshots.
"""

import asyncio
import json
import time

from game.world import World
from game.entities import Player
from game.config import HOST, PORT, TICK_RATE, MAP_W, MAP_H

world   = World()
clients = {}   # writer -> player_id

MOVE = {
    'w': (0, -1), 'k': (0, -1),
    's': (0,  1), 'j': (0,  1),
    'a': (-1, 0), 'h': (-1, 0),
    'd': (1,  0), 'l': (1,  0),
}


async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    player = Player(cls="warrior", name="New Employee")
    world.add_player(player)
    clients[writer] = player.id
    print(f"[+] {addr}  →  {player.name} [{player.id}]")

    try:
        while True:
            raw = await asyncio.wait_for(reader.readline(), timeout=120)
            if not raw:
                break
            try:
                msg = json.loads(raw.decode().strip())
            except json.JSONDecodeError:
                continue

            kind = msg.get("type")
            if kind == "input":
                key = msg.get("key", "")
                if key in MOVE:
                    dx, dy = MOVE[key]
                    world.move_player(player.id, dx, dy)
            elif kind == "set_name":
                player.name = str(msg.get("value", player.name))[:20]
                world.log(f"{player.name} updated their name badge.")
            elif kind == "set_cls":
                cls = msg.get("value", "warrior")
                if cls in ("warrior", "mage", "cleric"):
                    player.cls = cls
                    world.log(f"{player.name} switched role to {cls}.")

    except (asyncio.TimeoutError, ConnectionResetError, EOFError):
        pass
    finally:
        world.remove_player(player.id)
        clients.pop(writer, None)
        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
        print(f"[-] {addr} disconnected")


async def game_loop():
    interval = 1.0 / TICK_RATE
    vw = MAP_W - 2   # leave 1-cell border each side
    vh = MAP_H - 2

    while True:
        t0 = time.monotonic()
        world.tick()

        dead = []
        for writer, pid in list(clients.items()):
            try:
                state = world.state_for(pid, vw, vh)
                payload = (json.dumps(state) + "\n").encode()
                writer.write(payload)
                await writer.drain()
            except Exception:
                dead.append(writer)

        for w in dead:
            clients.pop(w, None)

        elapsed = time.monotonic() - t0
        await asyncio.sleep(max(0.0, interval - elapsed))


async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addrs  = ", ".join(str(s.getsockname()) for s in server.sockets)
    print(f"Office Terminal server  {addrs}  ({TICK_RATE} tps)")
    print(f"Dungeon: {len(world.rooms)} rooms generated")
    async with server:
        await asyncio.gather(server.serve_forever(), game_loop())


if __name__ == "__main__":
    asyncio.run(main())
