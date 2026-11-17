from enum import Enum, IntEnum

class ExitReason(IntEnum):
    UNKNOWN     = 0
    INGAME_QUIT = 1
    VICTORY     = 2

class MoveDirection(IntEnum):
    UP    = 0
    DOWN  = 1
    LEFT  = 2
    RIGHT = 3

class TileType(IntEnum):
    EMPTY  = 0
    SOLID  = 1
    BOX    = 2
    GOAL   = 4
    # to check if BOX and GOAL, tile == (BOX | GOAL)"
    PLAYER = 8

RendererCharacters: dict[int, str] = {
    TileType.EMPTY:   "  ",
    TileType.SOLID:   "██",
    TileType.BOX:     "[]",
    TileType.GOAL:    "╬╬",
    (TileType.BOX | TileType.GOAL): "!!", # box on top of goal
    TileType.PLAYER:  ":)"
}

# basic test map
DEFAULT_MAP = [
        [1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,1],
        [1,0,1,0,0,0,0,1],
        [1,0,0,2,0,0,0,1],
        [1,0,0,0,4,0,0,1],
        [1,0,0,0,0,6,0,1],
        [1,0,0,0,0,0,8,1],
        [1,1,1,1,1,1,1,1] ]
