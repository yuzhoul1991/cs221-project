"""A command line version of Minesweeper"""
import os
import random
import sys
from Player import Player
from Player import BaselineAIPlayer
from RLPlayer import RLPlayer
from csp import CspAIPlayer
from Grid import Grid

def main():
    # To be overridden
    if len(sys.argv) < 2:
        help_msg = """
        You need more input params! Sample usage:
        python game.py human (command line interface)
        python game.py gui (gui interface)
        python game.py baseline 10 10 10 - to start a baseline AI with 10*10 board with 10 mines
        python game.py baseline 10 10 10 100 - to start a baseline AI with 10*10 board with 10 mines, 100 times
        """
        print(help_msg)
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

    elif sys.argv[1] == 'gui':
        command = "python simulator.py human {} {} {}".format(*sys.argv[2:])
        print command
        os.system(command)

    elif sys.argv[1] == "baseline":
        num_run = 1 if len(sys.argv) < 6 else int(sys.argv[5])
        score = 0.0
        correct_moves = 0.0
        correct_mines = 0.0
        for _ in range(num_run):
            player = BaselineAIPlayer(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
            current_score, current_correct_moves, current_correct_mines = player.run()
            score += current_score
            correct_moves += current_correct_moves
            correct_mines += current_correct_mines
        print "Final score is: " + str(score / num_run)
        print "Average correct moves is: " + str(correct_moves / num_run)
        print "Average correct mines is: " + str(correct_mines / num_run)

    elif sys.argv[1] == "qlearning":
        num_run = 1 if len(sys.argv) < 6 else int(sys.argv[5])
        episodes = 10000 if len(sys.argv) < 7 else int(sys.argv[6])
        player = RLPlayer(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
        score, correct_moves, correct_mines = player.run(num_run, episodes)
        print "Final score is: " + str(score)
        print "Average correct moves is: " + str(correct_moves)
        print "Average correct mines is: " + str(correct_mines)

    elif sys.argv[1] == "csp":
        num_run = 1 if len(sys.argv) < 6 else int(sys.argv[5])
        score = 0.0
        correct_moves = 0.0
        correct_mines = 0.0
        for _ in range(num_run):
            print _
            player = CspAIPlayer(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
            current_score, current_correct_moves, current_correct_mines = player.run()
            score += current_score
            correct_moves += current_correct_moves
            correct_mines += current_correct_mines
        print "Final score is: " + str(score / num_run)
        print "Average correct moves is: " + str(correct_moves / num_run)
        print "Average correct mines is: " + str(correct_mines / num_run)

    elif sys.argv[1] == 'simulate':
        command = "python simulator.py simulate {}".format(sys.argv[2])
        print command
        os.system(command)

    elif sys.argv[1] == "compare":
        # Compare baseline and QLearning, on boards 4 * 4 and 10 * 10, with mine density = [0.1, 0.2, 0.4].
        # QLearning will train on each board 10000 times.
        num_run = 1000
        episodes = 10000
        for i in [5, 10]:
            for mine_density in [0.1, 0.15, 0.2, 0.3, 0.4]:
                num_mines = int(i * i * mine_density)
                # base line
                baseline_score = 0.0
                baseline_correct_moves = 0.0
                baseline_correct_mines = 0.0
                for _ in range(num_run):
                    player = BaselineAIPlayer(i, i, num_mines)
                    current_score, current_correct_moves, current_correct_mines = player.run(False)
                    baseline_score += current_score
                    baseline_correct_moves += current_correct_moves
                    baseline_correct_mines += current_correct_mines
                baseline_score = baseline_score / num_run
                baseline_correct_mines = baseline_correct_mines / num_run
                baseline_correct_moves = baseline_correct_moves / num_run
                # Q learning.
                player = RLPlayer(i, i, num_mines)
                qlearning_score, qlearning_correct_moves, qlearning_correct_mines = player.run(num_run, episodes, False)
                print "Size of the board: %d * %d; Number of mines: %d;" % (i, i, num_mines)
                print "Baseline score: %f; Q-Learning score: %f" % (baseline_score, qlearning_score)
                print "Baseline correct moves: %f; Q-Learning correct moves: %f" % (baseline_correct_moves, qlearning_correct_moves)
                print "Baseline correct mines: %f; Q-Learning correct mines: %f" % (baseline_correct_mines, qlearning_correct_mines)


if __name__ == '__main__':
    main()
