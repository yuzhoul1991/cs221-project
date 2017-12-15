import pdb
import sys
import random
import numpy as np
import tensorflow as tf
import math
from Player import AIPlayer
from RLPlayer import MiningMDP

class NNPlayerMDP(MiningMDP):
    def startBoardState(self):
        # 11 one hot channels: 0-8 for discovered tile number, 9 for discovered mine, 10 for undiscovered tiles
        # everything starts with undiscovered
        state = np.zeros((1, self.width, self.length, 11), dtype=np.float32)
        state[:,:,:,10] = 1
        return state

    def updateBoardState(self, player=None):
        if not player:
            player = self.player
        boardState = np.zeros((1, self.width, self.length, 11), dtype=np.float32)
        for y in range(self.length):
            for x in range(self.width):
                # discovered mine
                if player.currentPlayerBoard[x][y] == '-1':
                    boardState[0][x][y][9] = 1
                # undiscovered tile
                elif player.currentPlayerBoard[x][y] == 'x':
                    boardState[0][x][y][10] = 1
                # discovered numbered tile
                else:
                    boardState[0][x][y][int(player.currentPlayerBoard[x][y])] = 1
        return boardState

class NNPlayer(AIPlayer):
    def _create_placeholders(self, n_h0, n_w0, n_c0, n_y):
        X = tf.placeholder(tf.float32, shape=(None, n_h0, n_w0, n_c0), name='X')
        Y = tf.placeholder(tf.float32, shape=(n_y), name='Y')
        return X, Y

    def _initialize_parameters(self):
        tf.set_random_seed(self.seed)
        W1 = tf.get_variable("W1", [4, 4, 11, 64], initializer=tf.contrib.layers.xavier_initializer(seed=self.seed))
        W2 = tf.get_variable("W2", [4, 4, 64, 128], initializer=tf.contrib.layers.xavier_initializer(seed=self.seed))
        W3 = tf.get_variable("W3", [3, 3, 128, 256], initializer=tf.contrib.layers.xavier_initializer(seed=self.seed))
        parameters = {
            "W1" : W1,
            "W2" : W2,
            "W3" : W3,
        }
        return parameters

    def _forward_propagation(self, X, parameters):
        W1 = parameters['W1']
        W2 = parameters['W2']
        W3 = parameters['W3']

        Z1 = tf.nn.conv2d(X, W1, strides=[1,1,1,1], padding='SAME')
        A1 = tf.nn.relu(Z1)
        P1 = tf.nn.max_pool(A1, ksize=[1,4,4,1], strides=[1,4,4,1], padding='SAME')
        Z2 = tf.nn.conv2d(P1, W2, strides=[1,1,1,1], padding='SAME')
        A2 = tf.nn.relu(Z2)
        P2 = tf.nn.max_pool(A2, ksize=[1,4,4,1], strides=[1,4,4,1], padding='SAME')
        Z3 = tf.nn.conv2d(P2, W3, strides=[1,1,1,1], padding='SAME')
        A3 = tf.nn.relu(Z3)
        P3 = tf.nn.max_pool(A3, ksize=[1,3,3,1], strides=[1,3,3,1], padding='SAME')
        P3 = tf.contrib.layers.flatten(P3)
        Z4 = tf.contrib.layers.fully_connected(P3, 2*self.width*self.length, activation_fn=None)

        return Z4

    def _compute_cost(self, Z, Y):
        return tf.reduce_mean((Z-Y)**2)

    def getActionFromNNOutput(self, mdp, state, qvalues):
        legalActions = mdp.actions(state)
        values = list(qvalues)
        # FIXME: need fix when flag is added
        # (max qvalue, action, index in qvalues array from nn output)
        running_max = (float('-inf'), None, None)
        for action in legalActions:
            index = self.actionToQIndex(action)
            if values[index] > running_max[0]:
                running_max = values[index], action, index
        return running_max

    def actionToQIndex(self, action):
        word, x, y = action
        if word == "click":
            return y * self.width + x
        elif word == 'flag':
            return self.width * self.length + y*self.width + x

    def run(self, episodes=2000, save_log=True):
        explorationProb = 0.3
        mdp = NNPlayerMDP(self.length, self.width, self.num_mines)
        discount = mdp.discount()
        X, Y = self._create_placeholders(self.length, self.width, 11, self.length*self.width*2)
        parameters = self._initialize_parameters()
        # These qvalues include those for invalid actions needs filtering
        Z = self._forward_propagation(X, parameters)
        cost = self._compute_cost(Z, Y)
        trainer = tf.train.AdamOptimizer(learning_rate=0.004)
        updateModel = trainer.minimize(cost)

        init = tf.global_variables_initializer()
        saver = tf.train.Saver()

        if check_point_file:
            # try some games
            saver = tf.train.Saver()
            with tf.Session() as sess:
                saver.restore(sess, check_point_file)
                print("Model restored")

                score = 0.0
                for _ in range(100):
                    player = AIPlayer(self.length, self.width, self.num_mines)
                    boardState = mdp.startBoardState()
                    state = player
                    while not player.gameEnds():
                        allQ = sess.run(Z, feed_dict={X: boardState}).flatten()
                        boardState = mdp.updateBoardState(player)
                        _, nextAction, index = self.getActionFromNNOutput(mdp, state, allQ)
                        player.move(*nextAction)
                    score += player.score
                    print("Player score {}".format(player.score))
                print("Average score {}".format(score/100))
        else:
            with tf.Session() as sess:
                sess.run(init)
                for i in range(episodes):
                    if i % 100 == 0 and i != 0:
                        print("iteration: {}, loss: {}".format(i, running_cost))
                        save_path = saver.save(sess, "./ckpt/cnn_10_10_40.ckpt")
                        print("Checkpoint saved")
                    state = mdp.startState()
                    boardState = mdp.startBoardState()
                    while True:
                        # chose next action
                        allQ = sess.run(Z, feed_dict={
                            X: boardState
                        }).flatten()
                        _, nextAction, index = self.getActionFromNNOutput(mdp, state, allQ)
                        if random.random() < explorationProb:
                            nextAction = random.choice(mdp.actions(state))
                            index = self.actionToQIndex(nextAction)
                        # run the action through mdp to get new state and reward
                        newState, reward = mdp.succAndProbReward(state, nextAction)
                        newBoardState = mdp.updateBoardState()
                        if newState == None:
                            break

                        # get qvalue of new state from nn
                        allNextStateQ = sess.run(Z, feed_dict={
                            X: newBoardState
                        }).flatten()
                        maxQ = np.max(allNextStateQ)
                        #targetQ = np.zeros((1, 2*self.width*self.length), dtype=np.float32)
                        targetQ = allQ
                        targetQ[index] = reward + discount * maxQ

                        # do an iteration of backprop with the targetQ values
                        _, running_cost = sess.run([updateModel, cost], feed_dict={
                            X: boardState,
                            Y: targetQ
                        })

                        #print "Cost: {}".format(running_cost)


global check_point_file
if __name__ == '__main__':
    agent = NNPlayer(10, 10, 40)
    check_point_file = None
    if len(sys.argv) > 1:
        check_point_file = sys.argv[1]
    agent.run()
