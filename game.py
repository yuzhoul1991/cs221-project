"""A command line version of Minesweeper"""
import random
import sys

class Grid:
    def __init__(self, length, width, num_mines):
        self.board = [[0 for j in range(width)] for i in range(length)]
        self.length = length
        self.width = width
        self.num_mines = num_mines
        self.mines = []
        self.initialize_board()

    # sets a deterministic board - required to be the same l, w, num_mines as the initial one.
    # Could be called with setBoard(Grid(l, w, n_m).getBoard())
    def setBoard(self, board):
        self.board = board

    # Randomly initialize board given l, w, and num_mines
    def initialize_board(self):
        # First put mines on the board
        while len(self.mines) < self.num_mines:
            x = random.randrange(self.length)
            y = random.randrange(self.width)
            if (x, y) not in self.mines:
                self.mines.append((x, y))
            for x, y in self.mines:
                self.board[x][y] = -1
        # Update the remaining numbers:
        for i in range(self.length):
            for j in range(self.width):
                if self.board[i][j] == -1:
                    continue
                num_mines = 0
                for x in range(i - 1, i + 2):
                    for y in range(j - 1, j + 2):
                        if (x, y) in self.mines:
                            num_mines += 1
                            self.board[i][j] = num_mines

    # Returns a random mine that's not exposed to current board yet.
    def randomMine(self, currentMinesExplored):
        unexposed_mines = [m for m in self.mines if m not in currentMinesExplored]
        return random.choice(unexposed_mines)

    # Click / flag on the location (x, y) - returns -1 if clicks on the mine.
    def clickOn(self, x, y):
        return self.board[x][y]

    # return the current board
    def getBoard(self):
        return self.board

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
        return self.reward(x, y, -100, 1)

    # Returns value: reward in this action.
    def flag(self, x, y):
        return self.reward(x, y, self.length * self.width - self.num_moves + 30, -5)

    # Returns value: location of a random mine, reward in this action (-10)
    def hint(self):
        # No more mines to hint, we should return a very low reward.
        if len(self.currentMines) == self.num_mines:
            return self.currentMines[0], -100
        x, y = self.grid.randomMine(self.currentMines)
        self.currentPlayerBoard[x][y] = -1
        self.currentMines.append((x, y))
        self.num_moves += 1
        self.score -= 10
        return ((x, y), -10)

    def gameEnds(self):
        return self.num_moves == self.length * self.width

class AIPlayer(Player):
    # given action, return the reward.
    def move(action, x, y):
        if action == "hint":
            return self.hint()
        elif action == "click":
            return self.click(x, y)
        elif action == "flag":
            return self.flag(x, y)

def main():
    # To be overridden
    player = Player(1,1,1)
    while True:
        try:
            sys.stdout.write('>> ')
            line = sys.stdin.readline().strip()
            if not line:
                break
            args = line.split()
            if args[0] == "start":
                player = Player(int(args[1]), int(args[2]), int(args[3]))
            elif args[0] == "click":
                player.click(int(args[1]), int(args[2]))
                if player.gameEnds():
                    print "Final score: " + str(player.score)
                    break
            elif args[0] == "flag":
                player.flag(int(args[1]), int(args[2]))
                if player.gameEnds():
                    print "Final score: " + str(player.score)
                    break
            elif args[0] == "print":
                if len(args) > 1:
                    player.printCorrectBoard()
                else:
                    player.printPlayerBoard()
            elif args[0] == "hint":
                print player.hint()[0]
            elif args[0] == "score":
                print player.score
            elif args[0] == "quit":
                print "Final score: " + str(player.score)
                break
            else:
                print "unknown argument"
        except:
            print "invalid argument - try again"
main()