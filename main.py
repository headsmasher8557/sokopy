from enum import Enum, IntEnum
from copy import deepcopy
from Enum import MoveDirection, TileType, RendererCharacters
import sys  # sys.stdout.write is used instead of print for preference.
import os  # mostly for os.name on raw mode checks
import RawMode

if RawMode.enabled:
    if os.name == "posix":
        RawMode.posix_enable()
    elif os.name == "nt":
        pass
    else:
        print("Raw mode is enabled, but your OS doesnt support it")
        print("It will be disabled as a fallback")
        print("Press ENTER to continue")
        input("")
        RawMode.enabled = False

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

    def displaceTile(self, x: int, y: int, vx: int, vy: int, replaceTile=None, replacePrev=None):
        """ move a given tile x, y in the direction of vector vx, vy """
        here  = self.Map.getTileAt(x, y)
        there = self.Map.getTileAt(x+vx, y+vy)
        if there != TileType.EMPTY and there != TileType.GOAL:
            return False
        self.Map.setTileAt(x, y, replacePrev or TileType.EMPTY)
        self.Map.setTileAt(x+vx, y+vy, replaceTile or here)
        return True

    def step(self):
        promptstr = "enter a key (W,A,S,D,\x1b[4mR\x1b[0meset,e\x1b[4mX\x1b[0mit): "
        if RawMode.enabled:
            sys.stdout.write(promptstr)
            sys.stdout.flush()
        inp = None
        while not inp:
            try:
                if not RawMode.enabled:
                    i = input(promptstr).lstrip().lower()[-1]
                elif RawMode.enabled and os.name == "posix":
                    i = RawMode.posix_getch()
                elif RawMode.enabled and os.name == "nt":
                    i = RawMode.nt_getch()
                # HACK absolutely disgusting if
                if i == "w" or i == "a" or i == "s" or i == "d" or i == "r" or i == "x":
                    inp = i
                    break
            except:
                continue
        moveDir = None
        match inp:
            case "w":
                moveDir = MoveDirection.UP
            case "a":
                moveDir = MoveDirection.LEFT
            case "s":
                moveDir = MoveDirection.DOWN
            case "d":
                moveDir = MoveDirection.RIGHT
            case "r":
                self.reset()
            case "x":
                self.InProgress = False # quit
            case _:
                raise Exception("invalid char")
        self.move(moveDir)

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
                return -1
        # check end position
        endPx, endPy = self.Player.x + moveVector.x, self.Player.y + moveVector.y
        tile = self.Map.getTileAt(self.Player.x, self.Player.y)
        endTile = self.Map.getTileAt(endPx, endPy)
        if endTile == TileType.SOLID:
            return -1
        elif endTile == TileType.BOX:
            success = self.displaceTile(
                    endPx,
                    endPy,
                    moveVector.x,
                    moveVector.y,
                    (TileType.BOX | TileType.GOAL) if self.Map.getTileAt(endPx+moveVector.x, endPy+moveVector.y) == TileType.GOAL else TileType.BOX)
            if not success:
                return -1
        elif endTile == (TileType.BOX | TileType.GOAL):
            success = self.displaceTile(endPx, endPy, moveVector.x, moveVector.y, TileType.BOX, TileType.GOAL)
            if not success:
                return -1
        self.Moves += 1
        self.Player.x = endPx
        self.Player.y = endPy

    def renderWorld(self):
        for y in range(self.Map.Dimensions.y):
            for x in range(self.Map.Dimensions.x):
                if x == self.Player.x and y == self.Player.y:
                    sys.stdout.write(RendererCharacters[TileType.PLAYER])
                else:
                    sys.stdout.write(RendererCharacters[self.Map.getTileAt(x, y)])
            sys.stdout.write("\n")

    def render(self):
        """ render the game map and stats """
        sys.stdout.write(ANSI_CLEAR)
        # stats
        sys.stdout.write("MOVES: " + str(self.Moves)) # what other stats..?
        sys.stdout.write("\n" * 2)
        # world
        self.renderWorld()
        # flush changes
        sys.stdout.flush()

sys.stdout.write(ANSI_CLEAR)
sys.stdout.flush()
CurrentGame = Game(DEFAULT_MAP)
while CurrentGame.InProgress:
    CurrentGame.render()
    CurrentGame.step()

if os.name == "posix" and RawMode.enabled:
    RawMode.posix_restore()
