# -*- coding: UTF-8 -*-

import random

class Board():
    """
    A 2048 board
    """

    UP, DOWN, LEFT, RIGHT = 1, 2, 3, 4

    GOAL = 2048
    SIZE = 4

    def __init__(self, goal=GOAL, size=SIZE):
        self.__size = size
        self.__goal = goal
        self.__won = False
        self.cells = [[0]*self.__size for _ in xrange(self.__size)]
        self.addTile()
        self.addTile()

    def size(self):
        """
        return the board size
        """
        return self.__size

    def won(self):
        """
        return True if the board contains at least one tile with the board goal
        """
        return self.__won

    def canMove(self):
        """
        test if a move is possible
        """
        if not self.filled():
            return True

        for y in xrange(0, self.__size):
            for x in xrange(0, self.__size):
                c = self.getCell(x, y)
                if (x < self.__size-1 and c == self.getCell(x+1, y)) \
                        or (y < self.__size-1 and c == self.getCell(x, y+1)):
                    return True

        return False

    def filled(self):
        """
        return true if the game is filled
        """
        return len(self.getEmptyCells()) == 0

    def addTile(self, value=None, choices=[2, 4]):
        """
        add a random tile in an empty cell
          value: value of the tile to add.
          choices: a list of possible choices for the value of the tile.
                   default is [2, 4].
        """
        if value:
            choices = [value]

        v = random.choice(choices)
        empty = self.getEmptyCells()
        if empty:
            x, y = random.choice(empty)
            self.setCell(x, y, v)

    def getCell(self, x, y):
        """return the cell value at x,y"""
        return self.cells[y][x]

    def setCell(self, x, y, v):
        """set the cell value at x,y"""
        self.cells[y][x] = v

    def getLine(self, y):
        """return the y-th line, starting at 0"""
        return [self.getCell(i, y) for i in xrange(0, self.__size)]

    def getCol(self, x):
        """return the x-th column, starting at 0"""
        return [self.getCell(x, i) for i in xrange(0, self.__size)]

    def setLine(self, y, l):
        """set the y-th line, starting at 0"""
        for i in xrange(0, self.__size):
            self.setCell(i, y, l[i])

    def setCol(self, x, l):
        """set the x-th column, starting at 0"""
        for i in xrange(0, self.__size):
            self.setCell(x, i, l[i])

    def getEmptyCells(self):
        """return a (x, y) pair for each cell"""
        return [(x, y) for x in xrange(self.__size)
                           for y in xrange(self.__size) if self.getCell(x, y) == 0]

    def __collapseLineOrCol(self, line, d):
        """
        Merge tiles in a line or column according to a direction and return a
        tuple with the new line and the score for the move on this line
        """
        if (d == Board.LEFT or d == Board.UP):
            inc = 1
            rg = xrange(0, self.__size-1, inc)
        else:
            inc = -1
            rg = xrange(self.__size-1, 0, inc)

        pts = 0
        for i in rg:
            if line[i] == 0:
                continue
            if line[i] == line[i+inc]:
                v = line[i]*2
                if v == self.__goal:
                    self.__won = True

                line[i] = v
                line[i+inc] = 0
                pts += v

        return (line, pts)

    def __moveLineOrCol(self, line, d):
        """
        Move a line or column to a given direction (d)
        """
        nl = [c for c in line if c != 0]
        if d == Board.UP or d == Board.LEFT:
            return nl + [0] * (self.__size - len(nl))
        return [0] * (self.__size - len(nl)) + nl

    def move(self, d, add_tile=True):
        """
        move and return the move score
        """
        if d == Board.LEFT or d == Board.RIGHT:
            chg, get = self.setLine, self.getLine
        elif d == Board.UP or d == Board.DOWN:
            chg, get = self.setCol, self.getCol
        else:
            return 0

        moved = False
        score = 0

        for i in xrange(0, self.__size):
            origin = get(i)
            line = self.__moveLineOrCol(origin, d)
            collapsed, pts = self.__collapseLineOrCol(line, d)
            new = self.__moveLineOrCol(collapsed, d)
            chg(i, new)
            if origin != new:
                moved = True
            score += pts

        if moved and add_tile:
            self.addTile()

        return score
