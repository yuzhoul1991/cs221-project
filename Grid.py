import random

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