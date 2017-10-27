# cs221-project
Scoring mine sweeper ML project

python game.py
Actions: click, flag, hint, quit
To calculate score:
     click x,y: -100 if mine, +1 if not mine.
     flag x,y: +(30 + 棋盘剩余棋子数量) if mine, -5 if not mine
     hint: -10, gives a location of a mine.
     if (x,y) is already explored: -50 (so that we won't stuck in loop)
End: quit, or all the positions have been explored.

To interact with the file:
python game.py
Available commands:
start x y z: start a game with x*y and z mine.
click x y: click on x, y
hint: gives the location of a random mine.
flag x y: flag on x, y
score: current score
print: print current player board
print x: print the correct board (cheating :))
quit: quit the current game
