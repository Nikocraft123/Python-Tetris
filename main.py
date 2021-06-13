print("\n\nTetris Engine by Nikocraft")
print("--------------------------\n")
print("Author: Nikocraft")
print("Version: Beta 1.2")
print("Last Update: 4.5.2021")
print("\nLoad Packages:\n")


# IMPORTS

print("  - Time")
from time import sleep, time

print("  - Os")
import os

print("  - Sys")
import sys

print("  - Math")
import math

print("  - Get Opt")
import getopt as go

print("  - Date Time")
import datetime as dt

print("  - Py Game")
import pygame as pg

print("  - Json")
import json

print("  - Random")
import random as rd

print("\nPackages loaded\n")


# CLASSES

# Application
class Application:

    # CONSTRUCTOR
    def __init__(self, debug: bool = False):

        self.debug = debug

        if self.debug:
            self.appLogger = Logger("Tetris - APP", Logger.DEBUG)
        else:
            self.appLogger = Logger("Tetris - APP", Logger.INFO)

        try:
            with open(f"{resourcesPath}\\config.json", "r") as configFile:
                try:
                    self.configs = json.load(configFile)
                except json.JSONDecodeError:
                    self.appLogger.logWarning("Can't load the Config File. Reset all Settings and Statistics.\n", "File Loader")
                    os.remove(f"{resourcesPath}\\config.json")
                    self.configs = {}
                else:
                    self.appLogger.logInfo("Loaded the Config File.\n", "File Loader")
                configFile.close()
        except FileNotFoundError:
            self.appLogger.logWarning("Can't find the Config File. Reset all Settings and Statistics.\n", "File Loader")
            self.configs = {}

        self.appLogger.logDebug("Settings and Statistics:\n", "Config Manager")

        self.appLogger.logDebug("SETTINGS:", "Config Manager")
        if not "Settings" in self.configs:
            self.configs["Settings"] = {

            }
        for i in self.configs["Settings"]:
            self.appLogger.logDebug(f"- {i}: {self.configs['Settings'][i]}", "Config Manager")

        self.appLogger.logDebug("STATISTICS:", "Config Manager")
        if not "Statistics" in self.configs:
            self.configs["Statistics"] = {
                "Highscore": 0
            }
        for i in self.configs["Statistics"]:
            self.appLogger.logDebug(f"- {i}: {self.configs['Statistics'][i]}", "Config Manager")

        self.appLogger.logDebug("LATEST GAME:", "Config Manager")
        if not "Latest Game" in self.configs:
            self.configs["Latest Game"] = {
                "Grid": [0] * 20 * 10,
                "Speed": 2,
                "Score": 0,
                "Level": 1,
                "Active Figure": {}
            }
        for i in self.configs["Latest Game"]:
            self.appLogger.logDebug(f"- {i}: {self.configs['Latest Game'][i]}", "Config Manager")

        if self.debug:
            print("")


    # METHODS

    # Run
    def run(self) -> None:

        global app

        self.appLogger.logDebug("Initialize Menu ... \n", "App Manager")
        self.menu = self.Menu(app)

        self.appLogger.logDebug("Run new Game ... \n", "App Manager")
        self.menu.run()


    # CLASSES

    # Game
    class Game:

        # CONSTRUCTOR
        def __init__(self, app, grid: list[int] = None, speed: int = None, score: int = None, level: int = None, activeFigure: dict[str, object] = {}):

            self.app = app
            self.width = 300
            self.height = 680
            self.columns = 10
            self.lines = 20
            self.space = self.width // self.columns
            self.clock = pg.time.Clock()
            self.pause = False
            self.fps = 60
            self.speed = 2
            self.speedUpDelay = 30000
            self.level = 1
            self.score = 0
            self.activeFigureData = activeFigure
            self.time = 0

            if self.app.debug:
                self.gameLogger = Logger("Tetris - GAME", Logger.DEBUG)
            else:
                self.gameLogger = Logger("Tetris - GAME", Logger.INFO)

            self.grid = [0] * self.columns * self.lines

            if grid != None: self.grid = grid
            if speed != None: self.speed = speed
            if score != None: self.score = score
            if level != None: self.level = level

            self.gameLogger.logInfo("Initialize ...\n", "Launcher")
            self.gameLogger.logDebug("Game Settings: \n", "Settings")
            self.gameLogger.logDebug(f"Window width: {self.width}", "Settings")
            self.gameLogger.logDebug(f"Window height: {self.height}", "Settings")
            self.gameLogger.logDebug(f"Game lines: {self.lines}", "Settings")
            self.gameLogger.logDebug(f"Game columns: {self.columns}", "Settings")
            self.gameLogger.logDebug(f"Graphic fps: {self.fps}", "Settings")
            self.gameLogger.logDebug(f"Game Speed: {self.speed}", "Settings")
            self.gameLogger.logDebug(f"Game Speed Up Delay: {self.speedUpDelay}", "Settings")
            self.gameLogger.logDebug(f"Level: {self.level}", "Settings")
            self.gameLogger.logDebug(f"Score: {self.score}\n", "Settings")


        # CLASSES

        # Figure
        class Figure:

            _FigureTextures = [
                [8, 9, 10, 11],
                [0, 4, 5, 6],
                [1, 2, 6, 10],
                [5, 6, 9, 10],
                [1, 5, 6, 10],
                [1, 4, 5, 6],
                [4, 5, 9, 10],
            ]

            # CONSTRUCTOR
            def __init__(self, x: int, y: int, typeID: int, app, texture: list[int] = []):
                self.app = app
                self.x = x
                self.y = y
                self.type = typeID

                if texture == []:
                    self.texture = [0] * 16
                    for cell in self._FigureTextures[typeID - 1]:
                        self.texture[cell] = 1
                else:
                    self.texture = texture

                for cell, value in enumerate(self.texture):

                    if value == 0:
                        continue

                    x = cell % 4
                    y = cell // 4

                    if self.app.game.grid[x * self.app.game.columns + y] > 0:
                        self.app.game.gameOver()

            # METHODS

            # Draw
            def draw(self) -> None:

                for cell, value in enumerate(self.texture):

                    if value == 0:
                        continue

                    x = (self.x + cell % 4) * self.app.game.space
                    y = (self.y + cell // 4) * self.app.game.space

                    pg.draw.rect(self.app.game.screen, Color.getFigureColor(self.type), [x + (self.app.game.width // 2 - (self.app.game.space * self.app.game.columns) // 2), y + 50 + ((self.app.game.height - 80) % self.app.game.space) // 2, self.app.game.space, self.app.game.space])
                    pg.draw.rect(self.app.game.screen, Color.WHITE, [x + (self.app.game.width // 2 - (self.app.game.space * self.app.game.columns) // 2), y + 50 + ((self.app.game.height - 80) % self.app.game.space) // 2, self.app.game.space, self.app.game.space], 1)

            # Valid Change
            def validChange(self, xpos: int, ypos: int) -> bool:

                for cell, value in enumerate(self.texture):

                    if value == 0:
                        continue

                    x = xpos + cell % 4
                    y = ypos + cell // 4

                    if x < 0 or x >= self.app.game.columns or y >= self.app.game.lines or self.app.game.grid[y * self.app.game.columns + x] > 0:
                        return False

                return True

            # Rotate
            def rotate(self) -> None:

                textureCopy = self.texture.copy()

                for cell, value in enumerate(textureCopy):

                    x = cell % 4
                    y = cell // 4

                    self.texture[(2-x)*4+y] = value

                if not self.validChange(self.x, self.y):
                    self.texture = textureCopy.copy()
                    self.app.game.gameLogger.logDebug(f"Tried invalid rotation on active Figure.", "Game Loop")
                else:
                    self.app.game.gameLogger.logDebug(f"Rotated active Figure.", "Game Loop")

            # Move
            def move(self, xoff: int = 0, yoff: int = 0) -> bool:

                oldx = self.x
                oldy = self.y

                if self.validChange(self.x + xoff, self.y + yoff):

                    self.x += xoff
                    self.y += yoff

                    self.app.game.gameLogger.logDebug(f"Moved active Figure from ({oldx}|{oldy}) to ({self.x}|{self.y}).", "Game Loop")

                    return True

                self.app.game.gameLogger.logDebug(f"Tried invalid move on active Figure.", "Game Loop")

                return False

            # Freeze
            def freeze(self) -> None:

                for cell, value in enumerate(self.texture):

                    if value == 0:
                        continue

                    x = self.x + cell % 4
                    y = self.y + cell // 4

                    self.app.game.grid[y * self.app.game.columns + x] = self.type

            # Get Data
            def getData(self) -> dict[str, object]:
                return {
                    "x": self.x,
                    "y": self.y,
                    "typeID": self.type,
                    "texture": self.texture
                }


        # METHODS

        # Run
        def run(self) -> None:

            self.gameLogger.logInfo("Run ...\n", "Launcher")

            self.startTime = time()

            self.running = True

            self.gameLogger.logDebug("Initialize Py Game ...\n", "Start Routine")

            pg.init()

            self.gameLogger.logDebug("Open Window ...\n", "Start Routine")

            self.screen = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)
            pg.display.set_caption("Tetris - Game")

            pg.key.set_repeat(400, 80)

            self.gameLogger.logDebug("Register Custom Events ...\n", "Start Routine")

            self.tickEvent = pg.USEREVENT + 1
            self.tickSpeedUp = pg.USEREVENT + 2
            pg.time.set_timer(self.tickEvent, int(1000 / self.speed))
            pg.time.set_timer(self.tickSpeedUp, self.speedUpDelay)

            self.gameLogger.logDebug("Spawned new Figure.", "Game Loop")

            self.spawnFigure()

            while self.running:

                self.clock.tick(self.fps)

                self.time_start_test = time()

                self.width, self.height = pg.display.get_window_size()
                if self.width < self.space * self.columns:
                    self.width = self.space * self.columns
                if self.height < 670:
                    self.height = 670
                self.space = (self.height - 80) // self.lines
                self.screen = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)

                if self.pause:

                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            self.gameLogger.logDebug(f"Quit Button pressed.\n", "Input Manager")
                            self.quit(True)
                        if event.type == pg.KEYDOWN:
                            if event.key == pg.K_ESCAPE:
                                self.gameLogger.logDebug(f"Key Escape pressed.", "Key Input Manager")
                                self.gameLogger.logInfo(f"Game resumed.", "Pause Manager")
                                self.pause = False

                    self.updateScreen()

                    print(f"Time: {time() - self.time_start_test}")

                    continue

                for event in pg.event.get():

                    if event.type == self.tickEvent:
                        if not self.activeFigure.move(yoff=1):
                            self.gameLogger.logDebug("Frozed active Figure.", "Game Loop")
                            self.activeFigure.freeze()
                            self.score += self.checkFullLines()
                            self.gameLogger.logDebug("Spawned new Figure.", "Game Loop")
                            self.spawnFigure()
                    if event.type == self.tickSpeedUp:
                        oldSpeed = self.speed
                        self.speed = self.speed * 1.2
                        pg.time.set_timer(self.tickEvent, math.ceil(1000 // self.speed))
                        self.gameLogger.logDebug(f"Changed Game Speed from {oldSpeed} to {self.speed}.", "Game Loop")
                        self.level += 1
                        self.gameLogger.logInfo(f"Level Up! The Level is now {self.level}!", "Game Loop")

                    if event.type == pg.QUIT:
                        self.gameLogger.logDebug(f"Quit Button pressed.\n", "Input Manager")
                        self.quit(True)
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_ESCAPE:
                            self.gameLogger.logDebug(f"Key Escape pressed.", "Key Input Manager")
                            self.gameLogger.logInfo(f"Game paused.", "Pause Manager")
                            self.pause = True
                        if event.key == pg.K_UP or event.key == pg.K_w:
                            self.gameLogger.logDebug(f"Key Up or Key W pressed.", "Key Input Manager")
                            self.activeFigure.rotate()
                        if event.key == pg.K_DOWN or event.key == pg.K_s:
                            self.gameLogger.logDebug(f"Key Down or Key S pressed.", "Key Input Manager")
                            self.activeFigure.move(yoff=1)
                        if event.key == pg.K_LEFT or event.key == pg.K_a:
                            self.gameLogger.logDebug(f"Key Left or Key A pressed.", "Key Input Manager")
                            self.activeFigure.move(xoff=-1)
                        if event.key == pg.K_RIGHT or event.key == pg.K_d:
                            self.gameLogger.logDebug(f"Key Right or Key D pressed.", "Key Input Manager")
                            self.activeFigure.move(xoff=1)
                        if event.key == pg.K_RETURN:
                            self.gameLogger.logDebug(f"Key Enter pressed.", "Key Input Manager")
                            for i in range(1, 20):
                                if not self.activeFigure.move(yoff=1):
                                    break

                self.updateScreen()

                print(f"Time: {time() - self.time_start_test}")

        # Update Screen
        def updateScreen(self, gameOver: bool = False):

            self.screen.fill(Color.GRAY)

            self.activeFigure.draw()

            for cell, value in enumerate(self.grid):

                x = cell % self.columns * self.space
                y = cell // self.columns * self.space

                if value == 0:
                    pg.draw.rect(self.screen, Color.BLACK, [x + (self.width // 2 - (self.space * self.columns) // 2), y + 50 + ((self.height - 80) % self.space) // 2, self.space, self.space], 1)
                    continue

                pg.draw.rect(self.screen, Color.getFigureColor(value), [x + (self.width // 2 - (self.space * self.columns) // 2), y + 50 + ((self.height - 80) % self.space) // 2, self.space, self.space])
                pg.draw.rect(self.screen, Color.BLACK, [x + (self.width // 2 - (self.space * self.columns) // 2), y + 50 + ((self.height - 80) % self.space) // 2, self.space, self.space], 1)

            pg.draw.rect(self.screen, Color.BLACK, [2, 2, self.width - 4, 46], 3)
            textFont = pg.font.SysFont("Cambria", 16, False, True)
            numberFont = pg.font.SysFont("Century", 22, True, False)
            self.screen.blit(numberFont.render(str(self.score), True, Color.WHITE), (9, 3))
            self.screen.blit(numberFont.render(str(self.level), True, Color.WHITE), (self.width - 12 - numberFont.render(str(self.level), True, Color.WHITE).get_width(), 3))
            self.screen.blit(textFont.render("Score", True, Color.WHITE), (9, 24))
            self.screen.blit(textFont.render("Level", True, Color.WHITE), (self.width - 45, 24))

            pg.draw.rect(self.screen, Color.BLACK, [2, (self.height - 28), (self.width - 4), 26], 3)
            creditFont = pg.font.SysFont("$", 15, False, False)
            self.screen.blit(creditFont.render("Version: Beta 1.1", True, Color.WHITE), (9, (self.height - 19)))
            self.screen.blit(creditFont.render("Tetris", True, Color.WHITE), (self.width // 2 - creditFont.render("Tetris", True, Color.WHITE).get_width() // 2, (self.height - 19)))
            self.screen.blit(creditFont.render("Created by: Nikocraft", True, Color.WHITE), (self.width - 12 - creditFont.render("Created by: Nikocraft", True, Color.WHITE).get_width(), (self.height - 19)))

            if self.pause or gameOver:
                background = pg.Surface((self.width, self.height))
                background.set_alpha(90)
                background.fill(Color.BLACK)
                self.screen.blit(background, (0, 0))
                titleFont = pg.font.SysFont("Castellar", 60, True, False)

                if self.pause:
                    self.screen.blit(titleFont.render("Pause", True, Color.ORANGE), (self.width // 2 - titleFont.render("Pause", True, Color.RED).get_width() // 2, (self.height // 6)))
                    self.app.createButton(self.screen, 2001, "Resume Game", pg.mouse.get_pressed(), (self.width // 2 - 100), (self.height // 2 - 75 + 40), 200, 40, Color.PURPLE, Color.WHITE)
                    self.app.createButton(self.screen, 2004, "Restart Game", pg.mouse.get_pressed(), (self.width // 2 - 100), (self.height // 2 - 25 + 40), 200, 40, Color.BLACK, Color.WHITE)
                    self.app.createButton(self.screen, 2002, "Menu", pg.mouse.get_pressed(), (self.width // 2 - 100), (self.height // 2 + 25 + 40), 200, 40, Color.BLUE, Color.WHITE)
                    self.app.createButton(self.screen, 2003, "Quit App", pg.mouse.get_pressed(), (self.width // 2 - 100), (self.height // 2 + 75 + 40), 200, 40, Color.GREEN, Color.WHITE)

                if gameOver:
                    self.screen.blit(titleFont.render("Game", True, Color.RED), (self.width // 2 - titleFont.render("Game", True, Color.RED).get_width() // 2, (self.height // 8)))
                    self.screen.blit(titleFont.render("Over", True, Color.RED), (self.width // 2 - titleFont.render("Over", True, Color.RED).get_width() // 2, (self.height // 8) + 60))
                    self.app.createButton(self.screen, 3001, "Retry", pg.mouse.get_pressed(), (self.width // 2 - 100), (self.height // 2 - 50 + 40), 200, 40, Color.WHITE, Color.BLACK)
                    self.app.createButton(self.screen, 3002, "Menu", pg.mouse.get_pressed(), (self.width // 2 - 100), (self.height // 2 + 40), 200, 40, Color.YELLOW, Color.BLACK)
                    self.app.createButton(self.screen, 3003, "Quit App", pg.mouse.get_pressed(), (self.width // 2 - 100), (self.height // 2 + 50 + 40), 200, 40, Color.ORANGE, Color.BLACK)

            pg.display.flip()

        # Spawn Figure
        def spawnFigure(self) -> None:
            if self.activeFigureData == {}:
                # self.activeFigure = self.Figure(rd.randint(0, 6), 0, rd.randint(1, 7), self.app)
                self.activeFigure = self.Figure(rd.randint(0, 6), 0, 1, self.app)
            else:
                # self.activeFigure = self.Figure(self.activeFigureData["x"], self.activeFigureData["y"], self.activeFigureData["typeID"], self.app, self.activeFigureData["texture"])
                self.activeFigureData = {}

        # Check Full Lines
        def checkFullLines(self) -> int:

            clearedLines = 0

            for line in range(self.lines):

                for column in range(self.columns):
                    if self.grid[line * self.columns + column] == 0:
                        break
                else:
                    del self.grid[line * self.columns : line * self.columns + self.columns]
                    self.grid[0 : 0] = [0] * self.columns
                    clearedLines += 1

            points = clearedLines ** 2 * 100

            if clearedLines > 0:
                self.gameLogger.logDebug(f"Cleared {clearedLines} lines.", "Game Loop")
                self.gameLogger.logInfo(f"Earned {points} Points. Score: {self.score + points}", "Game Loop")

            return points

        # Game Over
        def gameOver(self) -> None:

            self.gameLogger.logInfo("Game Over!\n", "Game Loop")

            self.quit(False, True)

            self.app.menu.run()

        # Quit Game
        def quit(self, quitApp: bool = True, gameOver: bool = False) -> None:

            if not gameOver:
                self.gameLogger.logInfo(f"Quit Game ...\n", "Quit Routine")
                self.running = False
                self.gameLogger.logDebug("Quit Py Game ...\n", "Quit Routine")
                pg.quit()

            self.gameLogger.logInfo("Game Statistics: \n", "Statistics")
            self.gameLogger.logInfo(f"Final Score: {self.score} Points", "Statistics")
            self.gameLogger.logInfo(f"Final Level: {self.level}. Level", "Statistics")
            self.gameLogger.logInfo(f"Played Time: {math.ceil(time() - self.startTime)} Seconds", "Statistics")

            if self.score > self.app.configs["Statistics"]["Highscore"]:
                self.app.configs["Statistics"]["Highscore"] = self.score
                self.gameLogger.logInfo(f"NEW HIGHSCORE WITH {self.score}!!! :-D\n", "Statistics")
            else:
                self.gameLogger.logInfo(f"Your Highscore: {self.app.configs['Statistics']['Highscore']}\n", "Statistics")

            self.app.configs["Latest Game"]["Grid"] = self.grid
            self.app.configs["Latest Game"]["Speed"] = self.speed
            self.app.configs["Latest Game"]["Score"] = self.score
            self.app.configs["Latest Game"]["Level"] = self.level
            self.app.configs["Latest Game"]["Active Figure"] = self.activeFigure.getData()

            if quitApp:
                self.app.quit(False)

            if gameOver:
                self.app.configs["Latest Game"]["Grid"] = [0] * self.columns * self.lines
                self.app.configs["Latest Game"]["Speed"] = 2
                self.app.configs["Latest Game"]["Score"] = 0
                self.app.configs["Latest Game"]["Level"] = 1
                self.app.configs["Latest Game"]["Active Figure"] = {}

                while self.running:
                    self.clock.tick(self.fps)
                    self.width, self.height = pg.display.get_window_size()
                    if self.width < self.space * self.columns:
                        self.width = self.space * self.columns
                    if self.height < 670:
                        self.height = 670
                    self.space = (self.height - 80) // self.lines
                    self.screen = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)
                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            self.gameLogger.logDebug(f"Quit Button pressed.\n", "Input Manager")
                            self.gameLogger.logInfo(f"Quit Game ...\n", "Quit Routine")
                            self.running = False
                            self.gameLogger.logDebug("Quit Py Game ...\n", "Quit Routine")
                            pg.quit()
                            self.app.quit(False)
                    self.updateScreen(True)

                self.gameLogger.logDebug("Quit Py Game ...\n", "Quit Routine")
                pg.quit()

            self.app.menu = self.app.Menu(self.app)
            self.app.menu.run()

    # Menu
    class Menu:

        # CONSTRUCTOR
        def __init__(self, app):

            self.app = app
            self.width = 700
            self.height = 600
            self.clock = pg.time.Clock()
            self.fps = 60

            if self.app.debug:
                self.menuLogger = Logger("Tetris - MENU", Logger.DEBUG)
            else:
                self.menuLogger = Logger("Tetris - MENU", Logger.INFO)

            self.menuLogger.logInfo("Initialize ...\n", "Launcher")


        # METHODS

        # Run
        def run(self) -> None:

            self.menuLogger.logInfo("Run ...\n", "Launcher")

            self.running = True

            self.menuLogger.logDebug("Initialize Py Game ...\n", "Start Routine")

            pg.init()

            self.screen = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)
            pg.display.set_caption("Tetris - Menu")

            pg.key.set_repeat(400, 80)

            self.menuLogger.logDebug("Open Window ...\n", "Start Routine")

            while self.running:

                self.clock.tick(self.fps)

                self.time_start_test = time()

                self.width, self.height = pg.display.get_window_size()
                if self.width < 400:
                    self.width = 400
                if self.height < 500:
                    self.height = 500
                self.screen = pg.display.set_mode((self.width, self.height), pg.RESIZABLE)

                for event in pg.event.get():

                    if event.type == pg.QUIT:
                        self.menuLogger.logDebug(f"Quit Button pressed.\n", "Input Manager")
                        self.close()
                        self.app.quit(False)
                    if event.type == pg.KEYDOWN:
                        if event.key == pg.K_UP or event.key == pg.K_w:
                            self.menuLogger.logDebug(f"Key Up or Key W pressed.", "Key Input Manager")
                        if event.key == pg.K_DOWN or event.key == pg.K_s:
                            self.menuLogger.logDebug(f"Key Down or Key S pressed.", "Key Input Manager")

                self.updateScreen()

                print(f"Time: {time() - self.time_start_test}")

        # Update Screen
        def updateScreen(self):

            self.screen.fill(Color.GRAY)

            if self.app.configs["Latest Game"] == {"Grid": [0] * 20 * 10, "Speed": 2, "Score": 0, "Level": 1, "Active Figure": {}}:
                self.app.createButton(self.screen, 1001, "Play new Game", pg.mouse.get_pressed(), (self.width // 2 - 150), (self.height // 2 - 100 + 20), 300, 40, Color.GREEN, Color.WHITE)
            else:
                self.app.createButton(self.screen, 1001, "Play new Game", pg.mouse.get_pressed(), (self.width // 2 - 150), (self.height // 2 - 100 + 20), 148, 40, Color.GREEN, Color.WHITE)
                self.app.createButton(self.screen, 1007, "Continue Game", pg.mouse.get_pressed(), (self.width // 2 + 2), (self.height // 2 - 100 + 20), 148, 40, Color.GREEN, Color.WHITE)
            self.app.createButton(self.screen, 1002, "Options", pg.mouse.get_pressed(), (self.width // 2 - 150), (self.height // 2 - 50 + 20), 300, 40, Color.PINK, Color.BLACK)
            self.app.createButton(self.screen, 1003, "Statistics", pg.mouse.get_pressed(), (self.width // 2 - 150), (self.height // 2 + 20), 300, 40, Color.AQUA, Color.BLACK)
            self.app.createButton(self.screen, 1006, "Help", pg.mouse.get_pressed(), (self.width // 2 - 150), (self.height // 2 + 50 + 20), 300, 40, Color.YELLOW, Color.BLACK)
            self.app.createButton(self.screen, 1004, "Restart", pg.mouse.get_pressed(), (self.width // 2 - 150), (self.height // 2 + 100 + 20), 148, 40, Color.ORANGE, Color.BLACK)
            self.app.createButton(self.screen, 1005, "Quit", pg.mouse.get_pressed(), (self.width // 2 + 2), (self.height // 2 + 100 + 20), 148, 40, Color.ORANGE, Color.BLACK)
            self.app.createButton(self.screen, 1008, "Reset Application", pg.mouse.get_pressed(), (self.width - 160), (self.height - 60), 156, 26, Color.RED, Color.BLACK)

            titleFont = pg.font.SysFont("Castellar", 70, True, False)
            pg.draw.rect(self.screen, Color.BLUE, [(self.width // 2 - titleFont.render("Tetris", True, Color.ORANGE).get_width() // 2) - 12, (self.height // 8), 320, 76])
            pg.draw.rect(self.screen, Color.WHITE, [(self.width // 2 - titleFont.render("Tetris", True, Color.ORANGE).get_width() // 2) - 12, (self.height // 8), 320, 76], 4)
            self.screen.blit(titleFont.render("Tetris", True, Color.ORANGE), (self.width // 2 - titleFont.render("Tetris", True, Color.ORANGE).get_width() // 2, (self.height // 8)))

            pg.draw.rect(self.screen, Color.BLACK, [2, (self.height - 28), (self.width - 4), 26], 3)
            creditFont = pg.font.SysFont("$", 15, False, False)
            self.screen.blit(creditFont.render("Version: Beta 1.1", True, Color.WHITE), (9, (self.height - 19)))
            self.screen.blit(creditFont.render("Tetris", True, Color.WHITE), (self.width // 2 - creditFont.render("Tetris", True, Color.WHITE).get_width() // 2, (self.height - 19)))
            self.screen.blit(creditFont.render("Created by: Nikocraft", True, Color.WHITE), (self.width - 12 - creditFont.render("Created by: Nikocraft", True, Color.WHITE).get_width(), (self.height - 19)))

            pg.display.flip()

        # Close Menu
        def close(self) -> None:

            self.menuLogger.logInfo(f"Quit Menu ...\n", "Quit Routine")

            self.running = False

            self.menuLogger.logDebug("Quit Py Game ...\n", "Quit Routine")

            pg.quit()


    # METHODS

    # Create Button
    def createButton(self, screen: pg.Surface, id: int, text: str, click, x: int, y: int, width: int, height: int, color: tuple[int, int, int], textColor: tuple[int, int, int]):

        xcursor, ycursor = pg.mouse.get_pos()

        buttonFont = pg.font.SysFont("Baskerville Old Face Standard", 25, False, False)

        if xcursor > x and xcursor < x + width and ycursor > y and ycursor < y + height:
            active = True
            pg.draw.rect(screen, Color.modifyColor(color, (-70, -70, -70)), (x, y, width, height))
        else:
            active = False
            pg.draw.rect(screen, color, (x, y, width, height))

        pg.draw.rect(screen, Color.BLACK, (x, y, width, height), 2)

        screen.blit(buttonFont.render(text, True, textColor), ((x + width // 2 - buttonFont.render(text, True, textColor).get_width() // 2, height // 2 + y - 8)))

        global app

        if click[0] == 1 and active:

            if id == 1001:
                self.menu.menuLogger.logDebug(f"Play Button clicked.\n", "Button Input Manager")
                self.menu.close()
                self.game = self.Game(app)
                self.game.run()
            if id == 1002:
                self.menu.menuLogger.logDebug(f"Options Button clicked.\n", "Button Input Manager")
                pass
            if id == 1003:
                self.menu.menuLogger.logDebug(f"Statistics Button clicked.\n", "Button Input Manager")
                pass
            if id == 1004:
                self.menu.menuLogger.logDebug(f"Restart Button clicked.\n", "Button Input Manager")
                self.menu.close()
                self.quit(True)
            if id == 1005:
                self.menu.menuLogger.logDebug(f"Quit Button clicked.\n", "Button Input Manager")
                self.menu.close()
                self.quit()
            if id == 1006:
                self.menu.menuLogger.logDebug(f"Help Button clicked.\n", "Button Input Manager")
            if id == 1007:
                self.menu.menuLogger.logDebug(f"Play Button clicked.\n", "Button Input Manager")
                self.menu.close()
                self.game = self.Game(app, self.configs["Latest Game"]["Grid"], self.configs["Latest Game"]["Speed"], self.configs["Latest Game"]["Score"], self.configs["Latest Game"]["Level"], self.configs["Latest Game"]["Active Figure"])
                self.game.run()
            if id == 1008:
                self.menu.menuLogger.logDebug(f"Reset Application Button clicked.\n", "Button Input Manager")
                self.createPopUpMessage(screen, "Are you sure to reset the Application?", 200, 200, 0, 0, Color.ORANGE, Color.BLUE, Color.RED)
            if id == 2001:
                self.game.gameLogger.logDebug(f"Resume Button clicked.\n", "Button Input Manager")
                self.game.gameLogger.logInfo(f"Game resumed.", "Pause Manager")
                self.game.pause = False
            if id == 2002:
                self.game.gameLogger.logDebug(f"Menu Button clicked.\n", "Button Input Manager")
                self.game.quit(False)
            if id == 2003:
                self.game.gameLogger.logDebug(f"Quit Button clicked.\n", "Button Input Manager")
                self.game.quit(True)
            if id == 2004:
                self.game.gameLogger.logDebug(f"Restart Button clicked.\n", "Button Input Manager")
                self.game.gameLogger.logInfo(f"Quit Game ...\n", "Quit Routine")
                self.game.running = False
                self.game.gameLogger.logDebug("Quit Py Game ...\n", "Quit Routine")
                pg.quit()
                self.game = self.Game(app)
                self.game.run()
            if id == 3001:
                self.game.gameLogger.logDebug(f"Retry Button clicked.\n", "Button Input Manager")
                self.game.gameLogger.logInfo(f"Quit Game ...\n", "Quit Routine")
                self.game.running = False
                self.game.gameLogger.logDebug("Quit Py Game ...\n", "Quit Routine")
                pg.quit()
                self.game = self.Game(app)
                self.game.run()
            if id == 3002:
                self.game.gameLogger.logDebug(f"Restart Button clicked.\n", "Button Input Manager")
                self.game.gameLogger.logInfo(f"Quit Game ...\n", "Quit Routine")
                self.game.running = False
            if id == 3003:
                self.game.gameLogger.logDebug(f"Quit App Button clicked.\n", "Button Input Manager")
                self.game.gameLogger.logInfo(f"Quit Game ...\n", "Quit Routine")
                self.game.running = False
                self.game.gameLogger.logDebug("Quit Py Game ...\n", "Quit Routine")
                pg.quit()
                self.quit(False)

    # Create Pop Up Message
    def createPopUpMessage(self, screen: pg.Surface, text: str, x: int, y: int, level: int, buttonType: int, color: tuple[int, int, int], textColor: tuple[int, int, int], buttonColor: tuple[int, int, int]):

        surface = pg.Surface((200, 200))
        surface.set_colorkey(Color.BLACK)
        surface.set_alpha(200)
        surface.fill(color)
        titleFont = pg.font.SysFont(pg.font.get_default_font(), 20, False, False)
        surface.blit(titleFont.render(text, True, textColor), (5, 5))

        screen.blit(surface, (x, y))

    # Quit App
    def quit(self, doRestart: bool = False) -> None:

        with open(f"{resourcesPath}\\config.json", "w") as configFile:
            json.dump(self.configs, configFile, indent=4, separators=(',', ': '))
            configFile.close()
            self.appLogger.logInfo(f"Configs saved in the Config File at '{resourcesPath}\\config.json'!\n", "Config Manager")

        self.appLogger.logInfo("Quit Application ...\n", "Quit Routine")

        if doRestart:
            restart()

        sys.exit(0)


# Color
class Color:

    # VARIABLES

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (125, 125, 125)
    YELLOW = (255, 255, 0)
    ORANGE = (255, 195, 77)
    RED = (255, 0, 0)
    PURPLE = (128, 0, 255)
    PINK = (225, 77, 255)
    LIME = (77, 255, 77)
    GREEN = (0, 148, 49)
    AQUA = (25, 255, 255)
    BLUE = (0, 42, 255)
    _I = (0, 240, 240)         # I
    _J = (0, 0, 240)           # J
    _L = (240, 160, 0)         # L
    _O = (240, 240, 0)         # O
    _S = (0, 240, 0)           # S
    _T = (160, 0, 240)         # T
    _Z = (240, 0, 0)           # Z


    # METHODS

    # Get Form Color
    @classmethod
    def getFigureColor(cls, id: int) -> tuple[int, int, int]:

        figureColors = {
            1: cls._I,
            2: cls._J,
            3: cls._L,
            4: cls._O,
            5: cls._S,
            6: cls._T,
            7: cls._Z
        }

        return figureColors[id]

    # Modify Color
    @classmethod
    def modifyColor(cls, color: tuple[int, int, int], modifier: tuple[int, int, int]) -> tuple[int, int, int]:

        resultColor = [0, 0, 0]

        for rgb in range(0, 3):
            resultColor[rgb] = color[rgb] + modifier[rgb]
            if resultColor[rgb] > 255:
                resultColor[rgb] = 255
            if resultColor[rgb] < 0:
                resultColor[rgb] = 0

        return (resultColor[0], resultColor[1], resultColor[2])


# Logger
class Logger:

    # VARIABLES

    # Level
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


    # CONSTRUCTOR
    def __init__(self, domain: str, level: int = INFO, console: bool = True, files: list = [], logTime: bool = False):
        self.domain = domain
        self.level = level
        self.console = console
        self.files = files
        self.logTime = logTime


    # METHODS

    # Log Debug
    def logDebug(self, message: str, theme: str, tags: list[str] = [], showLevel: bool = True) -> bool:
        if self.level == self.DEBUG:
            self._log(message, theme, "DEBUG", tags, showLevel)
            return True
        return False

    # Log Info
    def logInfo(self, message: str, theme: str, tags: list[str] = [], showLevel: bool = True) -> bool:
        if self.level <= self.INFO:
            self._log(message, theme, "INFO", tags, showLevel)
            return True
        return False

    # Log Warning
    def logWarning(self, message: str, theme: str, tags: list[str] = [], showLevel: bool = True) -> bool:
        if self.level <= self.WARNING:
            self._log(message, theme, "WARNING", tags, showLevel)
            return True
        return False

    # Log Error
    def logError(self, message: str, theme: str, tags: list[str] = [], showLevel: bool = True) -> bool:
        if self.level <= self.ERROR:
            self._log(message, theme, "ERROR", tags, showLevel)
            return True
        return False

    # Log Critical
    def logCritical(self, message: str, theme: str, tags: list[str] = [], showLevel: bool = True) -> bool:
        self._log(message, theme, "INFO", tags, showLevel)
        return True

    # _Time
    def _time(self) -> str:
        return dt.datetime.now().strftime("%d/%b/%y %H:%M:%S")

    # _Log
    def _log(self, message: str, theme: str, level: str, tags: list[str], showLevel: bool) -> None:

        output = ""
        if self.logTime:
            output = output + f"[{self._time()} | {self.domain}] <{theme}> "
        else:
            output = output + f"[{self.domain}] <{theme}> "
        if showLevel:
            output = output + f"({level}) "
        for tag in tags:
            output = output + f"*{tag}* "
        output = output + message

        if self.console:
            print(output)
        for file in self.files:
            file.write(output + "\n")


# METHODS

# Restart
def restart() -> None:

    global app

    mainLogger.logInfo("Restart App System ... \n\n\n", "Launcher")

    sleep(1)

    if debugMode:
        mainLogger.logInfo("Initialize Application with Debug Mode ... \n", "Launcher")
    else:
        mainLogger.logInfo("Initialize Application ... \n", "Launcher")

    app = Application(debugMode)

    mainLogger.logInfo("Run Application ... \n", "Launcher")

    app.run()


# MAIN
if __name__ == '__main__':

    debugMode = False

    resourcesPath = "."

    invalidPath = False

    opts, args = go.getopt(sys.argv[1:], "do:")

    for opt, arg in opts:

        if opt == "-d":
            debugMode = True
        if opt == "-o":
            if (not os.path.exists(arg)) or arg[-1] != "\\":
                invalidPath = True
                continue
            resourcesPath = arg

    if debugMode:
        os.system("@title Tetris Engine by Nikocraft - Console - (Debug Mode)")
        mainLogger = Logger("Tetris - MAIN", Logger.DEBUG)
        mainLogger.logDebug("Debug Mode is activated!\n", "Console Argument Manager")
        mainLogger.logInfo("Initialize Application with Debug Mode ... \n", "Launcher")
    else:
        os.system("title Tetris Engine by Nikocraft - Console")
        mainLogger = Logger("Tetris - MAIN", Logger.INFO)
        mainLogger.logInfo("Initialize Application ... \n", "Launcher")

    app = Application(debugMode)

    mainLogger.logInfo("Run Application ... \n", "Launcher")

    app.run()
