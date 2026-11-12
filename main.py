from enum import Enum, IntEnum
from copy import deepcopy
from Vector2 import Vector2
from Tileset import Tileset
import Enum
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

ANSI_CLEAR = "\x1b[2J\x1b[3J\x1b[;H" # ANSI escape code for clearing display

class Game:
    Map = Tileset(Enum.DEFAULT_MAP)
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
        plr_x, plr_y = self.Map.findFirstTile(Enum.TileType.PLAYER)
        if plr_x == -1 and plr_y == -1:
            raise Exception("no player start found")
        self.Player.setXY(plr_x, plr_y)
        self.Map.setTileAt(plr_x, plr_y, Enum.TileType.EMPTY) # remove player spawn tile after spawning

    def displaceTile(self, x: int, y: int, vx: int, vy: int, replaceTile=None, replacePrev=None):
        """ move a given tile x, y in the direction of vector vx, vy """
        here  = self.Map.getTileAt(x, y)
        there = self.Map.getTileAt(x+vx, y+vy)
        if there != Enum.TileType.EMPTY and there != Enum.TileType.GOAL:
            return False
        self.Map.setTileAt(x, y, replacePrev or Enum.TileType.EMPTY)
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
                moveDir = Enum.MoveDirection.UP
            case "a":
                moveDir = Enum.MoveDirection.LEFT
            case "s":
                moveDir = Enum.MoveDirection.DOWN
            case "d":
                moveDir = Enum.MoveDirection.RIGHT
            case "r":
                self.reset()
            case "x":
                self.InProgress = False # quit
            case _:
                raise Exception("invalid char")
        self.move(moveDir)

    def move(self, direction: Enum.MoveDirection):
        moveVector = Vector2(0, 0)
        match direction:
            case Enum.MoveDirection.UP:
                moveVector.y = -1
            case Enum.MoveDirection.DOWN:
                moveVector.y = 1
            case Enum.MoveDirection.LEFT:
                moveVector.x = -1
            case Enum.MoveDirection.RIGHT:
                moveVector.x = 1
            case _:
                return -1
        # check end position
        endPx, endPy = self.Player.x + moveVector.x, self.Player.y + moveVector.y
        tile = self.Map.getTileAt(self.Player.x, self.Player.y)
        endTile = self.Map.getTileAt(endPx, endPy)
        if endTile == Enum.TileType.SOLID:
            return -1
        elif endTile == Enum.TileType.BOX:
            success = self.displaceTile(
                    endPx,
                    endPy,
                    moveVector.x,
                    moveVector.y,
                    (Enum.TileType.BOX | Enum.TileType.GOAL) if self.Map.getTileAt(endPx+moveVector.x, endPy+moveVector.y) == Enum.TileType.GOAL else Enum.TileType.BOX)
            if not success:
                return -1
        elif endTile == (Enum.TileType.BOX | Enum.TileType.GOAL):
            success = self.displaceTile(endPx, endPy, moveVector.x, moveVector.y, Enum.TileType.BOX, Enum.TileType.GOAL)
            if not success:
                return -1
        self.Moves += 1
        self.Player.x = endPx
        self.Player.y = endPy

    def renderWorld(self):
        for y in range(self.Map.Dimensions.y):
            for x in range(self.Map.Dimensions.x):
                if x == self.Player.x and y == self.Player.y:
                    sys.stdout.write(Enum.RendererCharacters[Enum.TileType.PLAYER])
                else:
                    sys.stdout.write(Enum.RendererCharacters[self.Map.getTileAt(x, y)])
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
CurrentGame = Game(Enum.DEFAULT_MAP)
while CurrentGame.InProgress:
    CurrentGame.render()
    CurrentGame.step()

if os.name == "posix" and RawMode.enabled:
    RawMode.posix_restore()
