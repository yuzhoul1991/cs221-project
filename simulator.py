import Tkinter as tk
import threading
import tkMessageBox
import random
import sys
from Grid import Grid
from Player import Player
from Player import BaselineAIPlayer

class Tile:
    images = {}
    @classmethod
    def import_images(klass):
        klass.images['tile_plain'] = tk.PhotoImage(file='images/tile_plain.gif')
        klass.images['tile_clicked'] = tk.PhotoImage(file="images/tile_clicked.gif")
        klass.images['tile_mine'] = tk.PhotoImage(file="images/tile_mine.gif")
        klass.images['tile_flag'] = tk.PhotoImage(file="images/tile_flag.gif")
        klass.images['tile_wrong'] = tk.PhotoImage(file="images/tile_wrong.gif")
        klass.images['tile_numbers'] = []
        klass.images['tile_numbers'].append(tk.PhotoImage(file='images/tile_clicked.gif'))
        for x in range(1, 9):
            klass.images['tile_numbers'].append(tk.PhotoImage(file='images/tile_'+str(x)+'.gif'))

    def __init__(self, frame, x, y, num):
        self.x = x
        self.y = y
        self.num = num
        self.is_mine = False if num != -1 else True
        self.img = self.images['tile_plain']
        self.btn = tk.Button(frame, image=self.img)

    def update_image(self):
        self.btn.config(image=self.img)

    def get_image(self, is_flag=False):
        if self.is_mine:
            return self.images['tile_flag'] if is_flag else self.images['tile_mine']
        else:
            return self.images['tile_numbers'][self.num]

    def click(self):
        print "click {} {}".format(self.x, self.y)
        self.img = self.get_image()
        self.update_image()

    def flag(self):
        print "flag {} {}".format(self.x, self.y)
        self.img = self.get_image(is_flag=True)
        self.update_image()

    def reveal(self):
        if not self.is_mine:
            raise RuntimeError, "Trying to reveal non mine tile, something is wrong"
        print "hint reveal {} {}".format(self.x, self.y)
        self.img = self.images['tile_mine']
        self.update_image()

class Gui:
    hint_btn_text = "Take Hint: (Remaining: {})"
    def __init__(self, root, player):
        self.tiles = []
        self.player = player
        self.root = root
        self.root.title("Minesweeper")
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.create_score_board()
        self.create_hint_btn()
        self.create_buttons()

    def run(self):
        self.root.mainloop()

    def create_hint_btn(self):
        self.hint_btn = tk.Button(self.frame, text=self.hint_btn_text.format(self.player.grid.num_mines))
        self.hint_btn.grid(row=1, column=0, columnspan=10)
        def hint_handler(event):
            (x, y), _ = self.player.hint()
            self.update_hint_remaining()
            self.tiles[x][y].reveal()
            self.update_score_board()
            if self.player.grid.num_mines - len(self.player.currentMines) == 0:
                self.hint_btn.unbind('<Button-1>')
        self.hint_btn.bind('<Button-1>', hint_handler)

    def update_hint_remaining(self):
        self.hint_btn.config(text=self.hint_btn_text.format(self.player.grid.num_mines - len(self.player.currentMines)))

    def create_score_board(self):
        self.score_board = tk.Label(self.frame, text="Score: 0")
        self.score_board.grid(row=0, column=0, columnspan=10)

    def update_score_board(self):
        self.score_board.config(text="Score: {}".format(self.player.score))

    def lclick_handler(self, x, y):
        def do_lclick(event):
            self.tiles[x][y].click()
            self.player.click(x, y)
            self.update_score_board()
            self.tiles[x][y].btn.unbind('<Button-1>')
            self.tiles[x][y].btn.unbind('<Button-2>')
        return do_lclick

    def rclick_handler(self, x, y):
        def do_rclick(event):
            self.tiles[x][y].flag()
            self.player.flag(x, y)
            self.update_score_board()
            self.tiles[x][y].btn.unbind('<Button-1>')
            self.tiles[x][y].btn.unbind('<Button-2>')
        return do_rclick

    def create_buttons(self):
        for i in range(0, self.player.length):
            self.tiles.append([])
            for j in range(0, self.player.width):
                self.tiles[i].append(Tile(self.frame, i, j, self.player.grid.board[i][j]))
                btn = self.tiles[i][j].btn
                btn.grid(row=i+2, column=j)
                btn.bind('<Button-1>', self.lclick_handler(i, j))
                btn.bind('<Button-2>', self.rclick_handler(i, j))

class Simulator(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.gui = gui

    def run(self):
        import time
        time.sleep(2)
        for i in range(0, self.gui.grid.length):
            for j in range(0, self.gui.grid.width):
                time.sleep(0.2)
                btn = self.gui.tiles[i][j].btn
                btn.focus_force()
                btn.event_generate("<Button-1>")

def main():
    if len(sys.argv) < 5:
        print "Sample usage:"
        print "python simulator.py AGENT LENGTH WIDTH MINES"
        print "Choice of AGENT: {human, baseline}"
        print "For example:"
        print "python simulator.py human 3 4 5"
        print "will create a 3 * 4 board with 5 mines, with human player."
        return
    if sys.argv[1] == "human":
        player = Player(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
        root = tk.Tk()
        Tile.import_images()
        gui = Gui(root, player)
        sim = Simulator(gui)
        #sim.start()
        gui.run()

if __name__ == '__main__':
    main()
