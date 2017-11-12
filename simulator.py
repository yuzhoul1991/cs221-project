import Tkinter as tk
import threading
import tkMessageBox
import random
from Grid import Grid

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

    def click(self):
        print "left click"
        if self.is_mine:
            self.img = self.images['tile_mine']
        else:
            self.img = self.images['tile_numbers'][self.num]
        self.btn.config(image=self.img)

    def flag(self):
        print "right click"
        self.img = self.images['tile_flag']
        self.btn.config(image=self.img)

class Gui:
    def __init__(self, root, grid):
        self.tiles = []
        self.grid = grid
        self.root = root
        self.root.title("Minesweeper")
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.title_label()
        self.create_buttons()

    def run(self):
        self.root.mainloop()

    def title_label(self):
        tk.Label(self.frame, text="MineSweeper").grid(row=0, column=0, columnspan=10)

    def lclick_handler(self, x, y):
        return lambda event: self.tiles[x][y].click()

    def rclick_handler(self, x, y):
        return lambda event: self.tiles[x][y].flag()

    def create_buttons(self):
        for i in range(0, grid.length):
            self.tiles.append([])
            for j in range(0, grid.width):
                self.tiles[i].append(Tile(self.frame, i, j, grid.board[i][j]))
                btn = self.tiles[i][j].btn
                btn.grid(row=i, column=j)
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


if __name__ == '__main__':
    grid = Grid(10, 10, 10)
    root = tk.Tk()
    Tile.import_images()
    gui = Gui(root, grid)
    sim = Simulator(gui)
    #sim.start()
    gui.run()
