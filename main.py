from sys import stdout # sys.stdout.write is used instead of print for preference.
from enum import Enum, IntEnum
import copy

# TODO: split this source code into different files its getting messy

ANSI_CLEAR = "\x1b[2J\x1b[3J\x1b[;H" # ANSI escape code for clearing display

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

class MoveDirection(IntEnum):
    UP    = 0
    DOWN  = 1
    LEFT  = 2
    RIGHT = 3

class TileType(IntEnum):
    EMPTY   = 0
    SOLID   = 1
    BOX     = 2
    GOAL    = 4
    # to check if BOX and GOAL, tile == (BOX | GOAL)"
    PLAYER  = 8

RendererCharacters: dict[int, str] = {
    TileType.EMPTY:   "  ",
    TileType.SOLID:   "██",
    TileType.BOX:     "[]",
    TileType.GOAL:    "╬╬",
    (TileType.BOX | TileType.GOAL): "{}", # box on top of goal
    TileType.PLAYER:  ":)"
}

class Vector2:
    x = 0
    y = 0

    def __init__(self, x=0, y=0):
        self.setXY(x, y)

    def setXY(self, x=None, y=None):
        self.x = x or self.x
        self.y = y or self.y

class Tileset:
    Map: list[list[int]] = DEFAULT_MAP
    Dimensions = Vector2(8, 8)
    MapArchive = None # Used in Game.reset for reloading maps

    def __init__(self, mapData=None):
        if not mapData:
            raise Exception("no mapdata")
        self.changeMap(mapData)

    def changeMap(self, mapData):
        self.MapArchive = mapData
        self.Map = copy.deepcopy(mapData)
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
        return self.Map[y][x]

    def setTileAt(self, x: int, y: int, v: int):
        self.Map[y][x] = v

    def findFirstTile(self, tileType: int) -> (int, int):
        for y in range(self.Dimensions.y):
            for x in range(self.Dimensions.x):
                if self.getTileAt(x, y) == tileType: return x, y
        return -1, -1

class Game:
    Map = Tileset(DEFAULT_MAP)
    Player = Vector2(0, 0)
    Moves = 0
    InProgress = False

    def __init__(self, gameMap):
        self.reset(gameMap)

    def reset(self, gameMap=None):
        self.Moves = 0
        self.InProgress = True
        self.Map.changeMap(gameMap or self.Map.MapArchive)
        # find first player spawn, ignore any subsequent ones. TODO decide if they should raise exceptions?
        plr_x, plr_y = self.Map.findFirstTile(TileType.PLAYER)
        if plr_x == -1 and plr_y == -1:
            raise Exception("no player start found")
        self.Player.setXY(plr_x, plr_y)
        self.Map.setTileAt(plr_x, plr_y, TileType.EMPTY) # remove player spawn tile after spawning

    def step(self):
        # HACK absolutely disgusting if
        inp = None
        while not inp:
            i = input("enter a key (W,A,S,D,\x1b[4mR\x1b[0meset,e\x1b[4mX\x1b[0mit): ").lstrip().lower()[0]
            if i == "w" or i == "a" or i == "s" or i == "d" or i == "r" or i == "x":
                inp = i
                break
        match inp:
            case "w":
                self.move(MoveDirection.UP)
            case "a":
                self.move(MoveDirection.LEFT)
            case "s":
                self.move(MoveDirection.DOWN)
            case "d":
                self.move(MoveDirection.RIGHT)
            case "r":
                self.reset()
            case "x":
                self.InProgress = False # quit

    def move(self, direction: MoveDirection):
        moveVector = Vector2(0, 0)
        match direction:
            case MoveDirection.UP:
                moveVector.y = -1
            case MoveDirection.DOWN:
                moveVector.y = 1
            case MoveDirection.LEFT:
                moveVector.x = -1
            case MoveDirection.RIGHT:
                moveVector.x = 1
            case _:
                raise Exception("invalid movedirection")
        # check end position
        endPx, endPy = self.Player.x + moveVector.x, self.Player.y + moveVector.y
        endTile = self.Map.getTileAt(endPx, endPy)
        if endTile == TileType.SOLID:
            return -1
        self.Moves += 1
        self.Player.x = endPx
        self.Player.y = endPy

    def renderWorld(self):
        for y in range(self.Map.Dimensions.y):
            for x in range(self.Map.Dimensions.x):
                if x == self.Player.x and y == self.Player.y:
                    stdout.write(RendererCharacters[TileType.PLAYER])
                else:
                    stdout.write(RendererCharacters[self.Map.getTileAt(x, y)])
            stdout.write("\n")

    def render(self):
        """ render the game map and stats """
        stdout.write(ANSI_CLEAR)
        # stats
        stdout.write("MOVES: " + str(self.Moves)) # what other stats..?
        stdout.write("\n" * 2)
        # world
        self.renderWorld()
        # flush changes
        stdout.flush()

stdout.write(ANSI_CLEAR)
stdout.flush()
CurrentGame = Game(DEFAULT_MAP)
while CurrentGame.InProgress:
    CurrentGame.render()
    CurrentGame.step()
