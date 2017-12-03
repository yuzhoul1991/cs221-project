import pdb
import random
import numpy as np
import tensorflow as tf
import math
from Player import AIPlayer
from RLPlayer import MiningMDP

class NNPlayerMDP(MiningMDP):
    def startBoardState(self):
        # use -100.0 for unexplored tile, -1 for mine other number 0-9 for number on the tile
        return np.array([[-2.0 for j in range(self.width)] for i in range(self.length)]).flatten()[:, np.newaxis]

    def updateBoardState(self, player=None):
        if not player:
            player = self.player
        state = np.array([[-2.0 for j in range(self.width)] for i in range(self.length)])
        for y in range(self.length):
            for x in range(self.width):
                if player.currentPlayerBoard[x][y] != 'x':
                    state[x][y] = player.currentPlayerBoard[x][y]
        return state.flatten()[:, np.newaxis]

class NNPlayer(AIPlayer):
    def _create_placeholders(self):
        input_states = tf.placeholder(tf.float32, shape=(self.input_dimension, 1), name='states')
        output = tf.placeholder(tf.float32, shape=(self.output_dimension, 1), name='label')
        return input_states, output

    def _initialize_parameters(self):
        # TODO: add parameterization so that can vary the number of hidden layers etc.
        middle_layer_size = int(1.5 * self.input_dimension)
        #W1 = tf.get_variable("W1", [middle_layer_size, self.input_dimension], initializer=tf.contrib.layers.xavier_initializer(seed=self.seed))
        #b1 = tf.get_variable("b1", [middle_layer_size, 1], initializer=tf.zeros_initializer())
        #W2 = tf.get_variable("W2", [self.output_dimension, middle_layer_size], initializer=tf.contrib.layers.xavier_initializer(seed=self.seed))
        W2 = tf.get_variable("W2", [self.output_dimension, self.input_dimension], initializer=tf.contrib.layers.xavier_initializer(seed=self.seed))
        b2 = tf.get_variable("b2", [self.output_dimension, 1], initializer=tf.zeros_initializer())

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




