from enum import Enum, IntEnum

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

# TODO consider if this should be moved to Game?
RendererCharacters: dict[int, str] = {
    TileType.EMPTY:   "  ",
    TileType.SOLID:   "██",
    TileType.BOX:     "[]",
    TileType.GOAL:    "╬╬",
    (TileType.BOX | TileType.GOAL): "!!", # box on top of goal
    TileType.PLAYER:  ":)"
}
