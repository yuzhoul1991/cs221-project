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
        self.num_flags_remaining = num_mines # Maximum number of flag option we can call

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
            return -float("inf")
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
        if self.num_flags_remaining == 0:
            return -float("inf")
        self.num_flags_remaining -= 1
        return self.reward(x, y, 30, -5)

    # Returns value: location of a random mine, reward in this action (-10)
    def hint(self):
        # No more mines to hint, we should return a very low reward.
        if len(self.currentMines) == self.num_mines:
            return None, -float("inf")
        x, y = self.grid.randomMine(self.currentMines)
        self.currentPlayerBoard[x][y] = -1
        self.currentMines.append((x, y))
        self.num_moves += 1
        self.score -= 3
        return ((x, y), -3)

    def gameEnds(self):
        return self.num_moves == self.length * self.width

class AIPlayer(Player):
    # Entry point to run the AI Player. To be overridden.
    def run(self):
        return

    # Returns move, x, y, based on the current board and last move (action, position (x,y), score). To be overridden.
    def chooseAction(self, last_action):
        return "quit", []

    def move(self, action, x, y):
        if action == "hint":
            return self.hint()
        elif action == "click":
            return self.click(x, y)
        elif action == "flag":
            return self.flag(x, y)

class BaselineAIPlayer(AIPlayer):
    def run(self):
        # A list of tuples (action, position), where we know for 100% which action to apply for each position. If this list is empty, we will explore randomly.
        self.known_tiles_to_explore = []
        a = self.chooseAction(None, None)
        # The agent might choose to quit, in the event that the best situation couldn't be further inferred.
        while a[0] != "quit" and not self.gameEnds():
            score = self.move(a[0], a[1], a[2])
            a = self.chooseAction(a[1], a[2])
        return self.score

    # @params: inputs are the position of last move.
    def chooseAction(self, last_x, last_y):
        # First, we define some simple rules based on the last action and the board.
        if last_x != None:
            # a list of positions that are neighbors of last action location and itself. At most 9.
            list_surrounding_tiles = [(x1, y1) for x1 in range(last_x - 1, last_x + 2) if x1 >= 0 and x1 < self.length for y1 in range(last_y - 1, last_y + 2) if y1 >= 0 and y1 < self.width]
            # A list of unknown tiles around last action location. At most 8.
            list_surrounding_unknown_tiles = [p for p in list_surrounding_tiles if self.currentPlayerBoard[p[0]][p[1]] == "x"]
            list_surrounding_mines = [p for p in list_surrounding_tiles if self.currentPlayerBoard[p[0]][p[1]] == -1]
            # 1. if we have already found all the mines around the tile, we should click on all the adjacent tiles.
            if self.currentPlayerBoard[last_x][last_y] - len(list_surrounding_mines) == 0:
                for x, y in list_surrounding_unknown_tiles:
                    if ("click", x, y) not in self.known_tiles_to_explore:
                        self.known_tiles_to_explore.append(("click", x, y))
            # 2. if the tile shows N + M, we have found M mines around the tile, and there are N tiles unknown arround the last tile, they should all be mines.
            elif self.currentPlayerBoard[last_x][last_y] - len(list_surrounding_mines) == len(list_surrounding_unknown_tiles):
                for x, y in list_surrounding_unknown_tiles:
                    if ("flag", x, y) not in self.known_tiles_to_explore:
                        self.known_tiles_to_explore.append(("flag", x, y))
            num_remaining_tiles = self.length * self.width - self.num_moves
            num_remaining_mines = self.num_mines - len(self.currentMines)
            # 3. if we have N tiles remaining and no more mines, the rest should all be click.
            if num_remaining_mines == 0:
                for x in range(self.length):
                    for y in range(self.width):
                        if self.currentPlayerBoard[x][y] == "x" and ("click", x, y) not in self.known_tiles_to_explore:
                            self.known_tiles_to_explore.append(("click", x, y))

            # 4. if we have N tiles remaining and N mines, the rest should all be flag.
            if num_remaining_mines == num_remaining_tiles:
                for x in range(self.length):
                    for y in range(self.width):
                        if self.currentPlayerBoard[x][y] == "x" and ("flag", x, y) not in self.known_tiles_to_explore:
                            self.known_tiles_to_explore.append(("flag", x, y))

        # If we know some tiles for sure, we will return that action and remove it from known tiles.
        if self.num_flags_remaining == 0:
            self.known_tiles_to_explore = [a for a in self.known_tiles_to_explore if a[0] != "flag"]

        if len(self.known_tiles_to_explore) != 0:
            result = self.known_tiles_to_explore[0]
            self.known_tiles_to_explore = self.known_tiles_to_explore[1:]
            return result

        # Finally, if none of the above rules apply, we will use random position.
        numRemainingMines = self.num_mines - len(self.currentMines)
        numRemainingCells = self.length * self.width - self.num_moves
        if numRemainingCells == 0:
            return "quit", []
        # Find a cell that we don't know yet.
        randomCell = (random.choice(range(self.length)), random.choice(range(self.width)))
        while self.currentPlayerBoard[randomCell[0]][randomCell[1]] != "x":
            randomCell = (random.choice(range(self.length)), random.choice(range(self.width)))
        chance_flag = float(numRemainingMines) / numRemainingCells
        if random.random() < chance_flag and self.num_flags_remaining > 0:
            return "flag", randomCell[0], randomCell[1]
        return "click", randomCell[0], randomCell[1]