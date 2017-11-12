"""A command line version of Minesweeper"""
import random
import sys
from game import Player

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
