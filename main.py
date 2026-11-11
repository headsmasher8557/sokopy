import sys # sys.stdout is used instead of print for preference.
from enum import Enum

DEFAULT_MAP = [
        [1,1,1,1,1,1,1,1],
        [1,4,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,1],
        [1,0,0,2,0,0,0,1],
        [1,0,0,0,0,0,0,1],
        [1,0,0,0,0,3,0,1],
        [1,0,0,0,0,0,0,1],
        [1,1,1,1,1,1,1,1] ]

MoveDirection: dict[str, int] = {
    UP    = 0
    DOWN  = 1
    LEFT  = 2
    RIGHT = 3
}

RendererCharacters: dict[int, str] = {
    0: " ",
    1: "#",
    2: "B",
    3: "G",
    4: "P"
}

class Vector2:
    x = 0
    y = 0
    def __init__(self, x, y):
        self.x = x or 0
        self.y = y or 0

class Tileset:
    Data: list[list[int]] = DEFAULT_MAP
    Dimensions = Vector2(8, 8)

    def __init__(self, mapData):
        if not mapData:
            return
        self.Data = mapData
        self.updateDimensions()

    def updateDimensions(self):
        """ update Tileset dimensions """
        self.Dimensions.x = 0
        self.Dimensions.y = len(self.Data)
        for y in range(len(self.Data)):
            row = self.Map[y]
            self.Dimensions.x = max(self.Dimensions.x, len(row))
            for x in range(len(row)):
                tile = row[x]
                # filter out invalid values
                if tile < 0 or tile > 4:
                    row[x] = 0

    def getTileAt(self, x: int, y: int) -> int:
        return self.Data[y][x]

    def setTileAt(self, x: int, y: int, v: int):
        self.Data[y][x] = v

    def findFirstTile(self, tileType: int) -> int, int:
        out_x = -1
        out_y = -1
        for y in range(self.Dimensions.y):
            for x in range(self.Dimensions.x):
                if self.getTileAt(x, y) == typeType:
                    out_x = x
                    out_y = y
                    break
        return out_x, out_y

class Game:
    Map = Tileset(DEFAULT_MAP)
    
    def __init__(self, gameMap):
        pass
