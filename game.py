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
                    if player.click(int(args[1]), int(args[2])) == -float("inf"):
                        print "Invalid Move! Already knows the location."
                    if player.gameEnds():
                        print "Final score: " + str(player.score)
                        break
                elif args[0] == "flag":
                    if player.flag(int(args[1]), int(args[2])) == -float("inf"):
                        print "Invalid Move! Already knows the location."
                    if player.gameEnds():
                        print "Final score: " + str(player.score)
                        break
                elif args[0] == "print":
                    if len(args) > 1:
                        player.printCorrectBoard()
                    else:
                        player.printPlayerBoard()
                elif args[0] == "hint":
                    pos = player.hint()[0]
                    if pos == None:
                        print "Invalid Move! Already knows the location."
                    print "Reveal mine pos:", pos
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
        episodes = 10000 if len(sys.argv) < 7 else int(sys.argv[6])
        player = RLPlayer(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
        score = player.run(num_run, episodes)
        print "Final score is: " + str(score)
    elif sys.argv[1] == "compare":
        # Compare baseline and QLearning, on boards i * i for i in [4, 7, 10, 13, 16], with mine density = [0.1, 0.3, 0.5, 0.7, 0.9].
        # QLearning will train on each board 10000 times.
        num_run = 1000
        episodes = 10000
        for i in range(4, 17, 3):
            for mine_density in range(1, 10, 2): # 0.1 to 0.9
                num_mines = i * i * mine_density / 10
                # base line
                baseline_score = 0
                for _ in range(num_run):
                    player = BaselineAIPlayer(i, i, num_mines)
                    baseline_score += player.run()
                baseline_score = baseline_score / float(num_run)
                # Q learning.
                player = RLPlayer(i, i, num_mines)
                qlearning_score = player.run(num_run, episodes)
                print "Size of the board: %d * %d; Number of mines: %d; Baseline score: %f; Q-Learning score: %f" % (i, i, num_mines, baseline_score, qlearning_score)


if __name__ == '__main__':
    main()
