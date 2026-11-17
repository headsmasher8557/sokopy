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
    ExitReason = Enum.ExitReason.UNKNOWN

    def __init__(self, gameMap):
        self.reset(gameMap)

    def reset(self, gameMap=None):
        ExitReason = Enum.ExitReason.UNKNOWN
        self.Moves = 0
        self.InProgress = True
        self.Map.changeMap(gameMap or self.Map.MapArchive)
        # find first player spawn, ignore any subsequent ones.
        plr_x, plr_y = self.Map.findFirstTile(Enum.TileType.PLAYER)
        if plr_x == -1 and plr_y == -1:
            # maybe its a PLAYER | GOAL?
            plr_x, plr_y = self.Map.findFirstTile(Enum.TileType.PLAYER | Enum.TileType.GOAL)
            if plr_x == -1 and plr_y == -1:
                raise Exception("no player start found")
            self.Map.setTileAt(plr_x, plr_y, Enum.TileType.GOAL)
        else:
            self.Map.setTileAt(plr_x, plr_y, Enum.TileType.EMPTY) # remove player spawn tile after spawning
        self.Player.setXY(plr_x, plr_y)

    # input handler

    def step(self):
        promptstr = "(W,A,S,D,\x1b[4mR\x1b[0meset,e\x1b[4mX\x1b[0mit): "
        if RawMode.enabled:
            sys.stdout.write("press a key " + promptstr)
            sys.stdout.flush()
        inp = None
        while not inp:
            try:
                if RawMode.enabled:
                    i = RawMode.getch()
                else:
                    i = input("enter a key " + promptstr).lstrip().lower()[-1]
                if i in ["w","a","s","d","r","x"]: # bit better than the if but shouldnt be hardcoded maybe?
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
                self.ExitReason = Enum.ExitReason.INGAME_QUIT
            case _:
                raise Exception("invalid char")
        self.move(moveDir)

    # game logic

    def displaceTile(self, x: int, y: int, vx: int, vy: int, replaceTile=None, replacePrev=None):
        """ move a given tile x, y in the direction of vector vx, vy """
        here  = self.Map.getTileAt(x, y)
        there = self.Map.getTileAt(x+vx, y+vy)
        if there != Enum.TileType.EMPTY and there != Enum.TileType.GOAL:
            return False
        self.Map.setTileAt(x, y, replacePrev or Enum.TileType.EMPTY)
        self.Map.setTileAt(x+vx, y+vy, replaceTile or here)
        return True

    def checkWin(self):
        """
            check if the player has won
            in short:
            - it will look at every tile in the map
            - if there exists at least ONE normal goal tile then the player hasnt won.
            some considerations to take:
            - it will NOT check if theres any remaining boxes on the map
        """
        for y in range(self.Map.Dimensions.y):
            for x in range(self.Map.Dimensions.x):
                if self.Map.getTileAt(x, y) == Enum.TileType.GOAL: return False
        return True

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
                    endPx, endPy,
                    moveVector.x, moveVector.y,
                    (Enum.TileType.BOX | Enum.TileType.GOAL) if self.Map.getTileAt(endPx+moveVector.x, endPy+moveVector.y) == Enum.TileType.GOAL else Enum.TileType.BOX)
            if not success:
                return -1
        elif endTile == (Enum.TileType.BOX | Enum.TileType.GOAL):
            success = self.displaceTile(
                    endPx, endPy,
                    moveVector.x, moveVector.y,
                    (Enum.TileType.BOX | Enum.TileType.GOAL) if self.Map.getTileAt(endPx+moveVector.x, endPy+moveVector.y) == Enum.TileType.GOAL else Enum.TileType.BOX,
                    Enum.TileType.GOAL)
            if not success:
                return -1
        self.Moves += 1
        self.Player.x = endPx
        self.Player.y = endPy
        if self.checkWin():
            self.onWin()

    def onWin(self):
        """ function called when the win condition is met """
        self.render() # make sure to let the player view the last frame before winning
        sys.stdout.write("YOU WON!!\n")
        sys.stdout.flush()
        self.InProgress = False
        self.ExitReason = Enum.ExitReason.VICTORY

    # renderer

    def renderMap(self):
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
        sys.stdout.write("MOVES: " + str(self.Moves))
        sys.stdout.write("\n")
        # world
        self.renderMap()
        # flush changes
        sys.stdout.flush()

import MapConverter

# bit of a helper class to help manage games and mostly the menu
class GameManager:
    CurrentGame = Game(Enum.DEFAULT_MAP)
    def mainMenu(self):
        PLRCHR = Enum.RendererCharacters[Enum.TileType.PLAYER]
        BOXCHR = Enum.RendererCharacters[Enum.TileType.BOX]
        GOLCHR = Enum.RendererCharacters[Enum.TileType.GOAL]
        TITLESTR =" SokoPy "
        FLAIRSTR = f"You're the {PLRCHR}, Push all the {BOXCHR} into the {GOLCHR}!"
        TITLESEPLEN = int(len(FLAIRSTR)/2) - int(len(TITLESTR)/2)
        sys.stdout.write(ANSI_CLEAR)
        sys.stdout.write(" " + "-" * TITLESEPLEN + TITLESTR + "-" * TITLESEPLEN + "\n")
        sys.stdout.write(" " + FLAIRSTR + "\n\n")
        sys.stdout.write(" 1 - Play the Microban I LevelSet\n")
        sys.stdout.write(" 2 - Play the Test Map\n")
        sys.stdout.write(" X - Exit\n")
        sys.stdout.flush()
        i = None
        while True:
            if RawMode.enabled:
                i = RawMode.getch().lower()
            else:
                i = input("enter a key: ").lower()
            if i == "1" or i == "2" or i == "x":
                break
        match i:
            case "1":
                levelset = MapConverter.convert_from_file("sets/microban1.txt")
                for level in levelset:
                    self.startGame(level)
                    sys.stdout.write("\n N - Next!\n X - Stop\n")
                    while True:
                        if RawMode.enabled:
                            i = RawMode.getch().lower()
                        else:
                            i = input("enter a key: ").lower()
                        if i == "n" or i == "x":
                            break
                    match i:
                        case "x":
                            break
                        case "n":
                            pass
            case "2":
                self.startGame(Enum.DEFAULT_MAP)
            case "x":
                return
        # post-game menu
        sys.stdout.write("\n M - Return to Main Menu\n")
        sys.stdout.write(" X - Exit\n")
        sys.stdout.flush()
        i = None
        while True:
            if RawMode.enabled:
                i = RawMode.getch().lower()
            else:
                i = input("enter a key: ").lower()
            if i == "m" or i == "x":
                break
        match i:
            case "m":
                return self.mainMenu()
            case "x":
                return

    def startGame(self, gameMap):
        self.CurrentGame.reset(gameMap)
        while self.CurrentGame.InProgress:
            self.CurrentGame.render()
            self.CurrentGame.step()

sys.stdout.write(ANSI_CLEAR)
sys.stdout.flush()
gameman = GameManager()
gameman.mainMenu()
if os.name == "posix" and RawMode.enabled:
    RawMode.posix_restore()
