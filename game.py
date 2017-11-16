"""A command line version of Minesweeper"""
import random
import sys
from Player import Player
from Player import BaselineAIPlayer
from RLPlayer import RLPlayer
from Grid import Grid

def main():
    # To be overridden
    if len(sys.argv) < 2:
        print "You need more input params! Sample usage:"
        print "python game.py human"
        print "python game.py baseline 10 10 10 - to start a baseline AI with 10*10 board with 10 mines"
        print "python game.py baseline 10 10 10 100 - to start a baseline AI with 10*10 board with 10 mines, 100 times"
        return
    if sys.argv[1] == "human":
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
    elif sys.argv[1] == "baseline":
        num_run = 1 if len(sys.argv) < 6 else int(sys.argv[5])
        score = 0
        for _ in range(num_run):
            player = BaselineAIPlayer(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
            score += player.run()
        print "Final score is: " + str(float(score) / num_run)
    elif sys.argv[1] == "qlearning":
        num_run = 1 if len(sys.argv) < 6 else int(sys.argv[5])
        player = RLPlayer(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
        score = player.run(num_run)
        print "Final score is: " + str(score)
    elif sys.argv[1] == "compare":
        # Compare baseline and QLearning, on boards i * j for i, j in [3, 6, 9, 12, 16], with mine density = [0.1, 0.25, 0.5, 0.7].
        # QLearning will train on each board 10000 times.
        num_run = 1000
        for i in [3, 6, 9, 12, 16]:
            for j in [3, 6, 9, 12, 16]:
                for mine_density in [0.1, 0.25, 0.5, 0.7]:
                    num_mines = int(i * j * mine_density)
                    # base line
                    baseline_score = 0
                    for _ in range(num_run):
                        player = BaselineAIPlayer(i, j, num_mines)
                        baseline_score += player.run()
                    baseline_score = baseline_score / float(num_run)
                    # Q learning.
                    player = RLPlayer(i, j, num_mines)
                    qlearning_score = player.run(num_run)
                    print "Size of the board: %d * %d; Number of mines: %d; Baseline score: %f; Q-Learning score: %f" % (i, j, num_mines, baseline_score, qlearning_score)


if __name__ == '__main__':
    main()
