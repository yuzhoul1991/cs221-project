import pdb
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
        state = np.zeros(self.width, self.length, 11)
        state[:,:,10] = 1
        return state

    def updateBoardState(self, player=None):
        if not player:
            player = self.player
        boardState = np.zeros(self.width, self.length, 11)
        for y in range(self.length):
            for x in range(self.width):
                # discovered mine
                if player.currentPlayerBoard[x][y] == '-1':
                    boardState[x][y][9] = 1
                # undiscovered tile
                elif player.currentPlayerBoard[x][y] == 'x': 
                    boardState[x][y][10] = 1
                # discovered numbered tile
                else:
                    boardState[x][y][int(player.currentPlayerBoard[x][y])] = 1
        return boardState

class NNPlayer(AIPlayer):
    def _create_placeholders(self, n_h0, n_w0, n_c0, n_y):
        X = tf.placeholder(tf.float32, shape=(None, n_h0, n_w0, n_c0), name='X')
        Y = tf.placeholder(tf.float32, shape=(None, n_y), name='Y')
        return X, Y

    def _initialize_parameters(self):
        tf.set_random_seed(self.seed)
        W1 = tf.get_variable("W1", [4, 4, 11, 64], initializer=tf.contrib.layers.xavier_initializer(seed=self.seed))
        W2 = tf.get_variable("W2", [4, 4, 11, 64], initializer=tf.contrib.layers.xavier_initializer(seed=self.seed))
        parameters = {
            #"W1" : W1,        
            #"b1" : b1,        
            "W2" : W2,        
            "b2" : b2,        
        }
        return parameters

    def _forward_propagation(self, X, parameters):
        #Z1 = tf.add(tf.matmul(parameters['W1'], X), parameters['b1'])
        #A1 = tf.nn.relu(Z1)
        #Z2 = tf.add(tf.matmul(parameters['W2'], A1), parameters['b2'])
        #return Z2
        return tf.matmul(parameters['W2'], X)

    def _compute_cost(self, Z, Y):
        return tf.reduce_mean(tf.square(Y - Z))
        #logits = tf.transpose(Z)
        #return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=tf.transpose(Y)))

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

    def run(self, episodes=1000, save_log=True):
        explorationProb = 0.5
        mdp = NNPlayerMDP(self.length, self.width, self.num_mines)
        discount = mdp.discount()
        self.input_dimension = self.length * self.width
        self.output_dimension = self.input_dimension * 2
        X, Y = self._create_placeholders()
        parameters = self._initialize_parameters()
        # These qvalues include those for invalid actions needs filtering
        predictedQvalues = self._forward_propagation(X, parameters)
        cost = self._compute_cost(predictedQvalues, Y)
        trainer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
        updateModel = trainer.minimize(cost)
        
        init = tf.initialize_all_variables()
        with tf.Session() as sess:
            sess.run(init)
            for i in range(episodes):
                if i % 100 == 0 and i != 0:
                    print "iteration: {}, loss: {}".format(i, running_cost)
                state = mdp.startState()
                boardState = mdp.startBoardState()
                while True:
                    # chose next action
                    allQ = sess.run(predictedQvalues, feed_dict={
                        X: boardState
                    })
                    _, nextAction, index = self.getActionFromNNOutput(mdp, state, allQ)
                    if random.random() < explorationProb:
                        nextAction = random.choice(mdp.actions(state))
                        index = self.actionToQIndex(nextAction)
                    # run the action through mdp to get new state and reward
                    newState, reward = mdp.succAndProbReward(state, nextAction)
                    newBoardState = mdp.updateBoardState()
                    if newState == None:
                        break
                    #print newBoardState

                    # get qvalue of new state from nn

                    allNextStateQ = sess.run(predictedQvalues, feed_dict={
                        X: newBoardState
                    })
                    maxQ = np.max(allNextStateQ)
                    targetQ = allQ
                    targetQ[index] = reward + discount * maxQ
                    
                    #pdb.set_trace()

                    # do an iteration of backprop with the targetQ values
                    _, running_cost = sess.run([updateModel, cost], feed_dict={
                        X: boardState,
                        Y: targetQ
                    })

                    #print "Cost: {}".format(running_cost)

            # try some games
            score = 0.0
            for _ in range(100):
                player = AIPlayer(self.length, self.width, self.num_mines)
                boardState = mdp.startBoardState()
                state = player
                while not player.gameEnds():
                    allQ = sess.run(predictedQvalues, feed_dict={X: boardState})
                    boardState = mdp.updateBoardState(player)
                    _, nextAction, index = self.getActionFromNNOutput(mdp, state, allQ)
                    player.move(*nextAction)
                score += player.score
            print "Average score {}".format(score/100)



if __name__ == '__main__':
    agent = NNPlayer(5, 5, 3)
    agent.run()




