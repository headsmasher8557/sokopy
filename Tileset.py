from Vector2 import Vector2
from copy import deepcopy
import Enum

class Tileset:
    Map: list[list[int]] = Enum.DEFAULT_MAP
    Dimensions = Vector2(8, 8)
    MapArchive = None # Used in Game.reset for reloading maps

    def __init__(self, mapData=None):
        if not mapData:
            raise Exception("no mapdata")
        self.changeMap(mapData)

    def changeMap(self, mapData):
        self.MapArchive = mapData
        self.Map = deepcopy(mapData)
        self.updateDimensions()

    def updateDimensions(self):
        self.Dimensions.x = 0
        self.Dimensions.y = len(self.Map)
        for y in range(len(self.Map)):
            row = self.Map[y]
            self.Dimensions.x = max(self.Dimensions.x, len(row))
            for x in range(len(row)):
                tile = row[x]
                # filter out invalid values
                if tile < 0 or tile > 9:
                    row[x] = 0

    def getTileAt(self, x: int, y: int) -> int:
        row = self.Map[y]
        return row[x] if x < len(row) else Enum.TileType.EMPTY

    def setTileAt(self, x: int, y: int, v: int):
        self.Map[y][x] = v

    def findFirstTile(self, tileType: int) -> (int, int):
        for y in range(self.Dimensions.y):
            for x in range(self.Dimensions.x):
                if self.getTileAt(x, y) == tileType: return x, y
        return -1, -1
