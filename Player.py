"""A command line version of Minesweeper"""
import random
from Grid import Grid

class Player:
    def __init__(self, length, width, num_mines):
        self.grid = Grid(length, width, num_mines)
        self.length = length
        self.width = width
        self.num_mines = num_mines
        self.currentPlayerBoard = [["x" for j in range(width)] for i in range(length)]
        self.currentMines = []
        self.num_moves = 0
        self.score = 0

    def setBoard(self, board):
        self.grid.setBoard(board)

    # For debugging only.
    def printCorrectBoard(self):
        for l in self.grid.getBoard():
            list_string = [str(i) for i in l]
            print " ".join(list_string)

    # For debugging only.
    def printPlayerBoard(self):
        for l in self.currentPlayerBoard:
            list_string = [str(i) for i in l]
            print " ".join(list_string)

    # general function to calculate reward on x, y
    def reward(self, x, y, reward_for_mine, reward_for_normal):
        # Already explored, so we should return a low reward to prevent clicking again.
        if str(self.currentPlayerBoard[x][y]) != "x":
            self.score -= 50
            return -50
        self.currentPlayerBoard[x][y] = self.grid.clickOn(x, y)
        self.num_moves += 1
        if self.currentPlayerBoard[x][y] == -1:
            self.score += reward_for_mine
            self.currentMines.append((x, y))
            return reward_for_mine
        self.score += reward_for_normal
        return reward_for_normal

    # Returns value: reward in this action.
    def click(self, x, y):
        return self.reward(x, y, -20, 1)

    # Returns value: reward in this action.
    def flag(self, x, y):
        return self.reward(x, y, self.length * self.width - self.num_moves + 30, -5)

    # Returns value: location of a random mine, reward in this action (-10)
    def hint(self):
        # No more mines to hint, we should return a very low reward.
        if len(self.currentMines) == self.num_mines:
            return self.currentMines[0], -50
        x, y = self.grid.randomMine(self.currentMines)
        self.currentPlayerBoard[x][y] = -1
        self.currentMines.append((x, y))
        self.num_moves += 1
        self.score -= 3
        return ((x, y), -3)

    def gameEnds(self):
        return self.num_moves == self.length * self.width

class AIPlayer(Player):
	def run(self):
		a = self.chooseAction()
		# The agent might choose to quit, in the event that the best situation couldn't be further inferred.
		while a[0] != "quit" and not self.gameEnds():
			score = self.move(a[0], a[1], a[2]) # score might be useful for q-learning reward calculation.
			a = self.chooseAction()
		return self.score

	# Returns move, x, y, based on the current board. To be overridden.
	def chooseAction(self):
		return "quit", []

	def move(self, action, x, y):
		if action == "hint":
			return self.hint()
		elif action == "click":
			return self.click(x, y)
		elif action == "flag":
			return self.flag(x, y)

class BaselineAIPlayer(AIPlayer):
	def chooseAction(self):
		numRemainingMines = self.num_mines - len(self.currentMines)
		numRemainingCells = self.length * self.width - self.num_moves
		if numRemainingCells == 0:
			return "quit", []
		# Find a cell that we don't know yet.
		randomCell = (random.choice(range(self.length)), random.choice(range(self.width)))
		while self.currentPlayerBoard[randomCell[0]][randomCell[1]] != "x":
			randomCell = (random.choice(range(self.length)), random.choice(range(self.width)))
		chance_flag = float(numRemainingMines) / (numRemainingMines + numRemainingCells)
		if random.random() < chance_flag:
			return "flag", randomCell[0], randomCell[1]
		return "click", randomCell[0], randomCell[1]
