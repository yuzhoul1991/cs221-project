import math, random
from collections import defaultdict
from Player import AIPlayer

# Performs Q-learning.  Read util.RLAlgorithm for more information.
# actions: a function that takes a state and returns a list of actions.
# discount: a number between 0 and 1, which determines the discount factor
# featureExtractor: a function that takes a state and action and returns a list of (feature name, feature value) pairs.
# explorationProb: the epsilon value indicating how frequently the policy
# returns a random action
class QLearningAlgorithm:
    def __init__(self, actions, discount, featureExtractor, explorationProb=1):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = defaultdict(float)
        self.numIters = 0

    # Return the Q function associated with the weights and features
    def getQ(self, state, action):
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    # Instead of completely random actions, it will choose random actions based on probability.
    def getAction(self, state, random_flag_prob):
        self.numIters += 1
        if random.random() < self.explorationProb:
            all_choices = self.actions(state)
            click_choices = [i for i in all_choices if i[0] == "click"]
            flag_choices = [i for i in all_choices if i[0] ==  "flag"]
            if random.random() < random_flag_prob:
                return random.choice(flag_choices)
            return random.choice(click_choices)
        else:
            l = [(self.getQ(state, action), action) for action in self.actions(state)]
            max_weight = max(l)[0]
            click_choices = [i for i in l if i[0] == max_weight and i[1][0] == "click"]
            flag_choices = [i for i in l if i[0] == max_weight and i[1][0] == "flag"]
            if random.random() < random_flag_prob:
                return random.choice(flag_choices)[1]
            return random.choice(click_choices)[1]

    # Call this function to get the step size to update the weights.
    def getStepSize(self):
        return 1.0 / math.sqrt(self.numIters)

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state, action, reward, newState):
        v_opt = 0
        if newState != None:
          v_opt = max(self.getQ(newState, a) for a in self.actions(newState))
        q_value = self.getQ(state, action)
        factor = (q_value - reward - self.discount * v_opt) * self.getStepSize()
        for f, v in self.featureExtractor(state, action):
            self.weights[f] -= factor

# Naive FeatureExtractor. Doesn't perform well in a large Grid.
def identityFeatureExtractor(state, action):
    # First serialize state to a string, so that it's hashable:
    string_state = ''.join([''.join(str(e) for e in i) for i in state])
    featureKey = (string_state, action)
    featureValue = 1
    return [(featureKey, featureValue)]

# Helper function to find the probability of mine in the player's current board.
def ProbabilityMine(player):
    numRemainingMines = player.num_mines - len(player.currentMines)
    numRemainingCells = player.length * player.width - player.num_moves
    return float(numRemainingMines) / numRemainingCells

# State is the current player board.
class ChessMDP:
    def __init__(self, length, width, num_mines):
        self.length = length
        self.width = width
        self.num_mines = num_mines

    # Each time we start a new state, we will create a new game.
    def startState(self):
        self.player = AIPlayer(self.length, self.width, self.num_mines)
        return self.player.currentPlayerBoard

    def actions(self, state):
        result = []
        for x in range(len(state)):
            for y in range(len(state[0])):
                if state[x][y] == "x":
                    result.append(("click", x, y))
                    result.append(("flag", x, y))
        return result

    # Unlike homework, this will only have a deterministic successor.
    # Returns successor and the reward.
    def succAndProbReward(self, state, action):
        score = self.player.move(action[0], action[1], action[2])
        if self.player.gameEnds():
            return None, None
        return self.player.currentPlayerBoard, score

    def discount(self):
        return 0.9

def simulate(mdp, rl, numTrials=1000, maxIterations=300):
    totalRewards = []  # The rewards we get on each trial
    for trial in range(numTrials):
        if trial % 1000 == 0:
            print trial
        state = mdp.startState()
        totalDiscount = 1
        totalReward = 0
        for _ in range(maxIterations):
            action = rl.getAction(state, ProbabilityMine(mdp.player))
            newState, reward = mdp.succAndProbReward(state, action)
            if newState == None:
                rl.incorporateFeedback(state, action, 0, None)
                break
            # Choose a random transition
            rl.incorporateFeedback(state, action, reward, newState)
            totalReward += totalDiscount * reward
            totalDiscount *= mdp.discount()
            state = newState
        totalRewards.append(totalReward)
    return totalRewards


class RLPlayer(AIPlayer):
    def run(self, num_times):
        # It will first train itself.
        mdp = ChessMDP(self.length, self.width, self.num_mines)
        rl = QLearningAlgorithm(mdp.actions, mdp.discount(), identityFeatureExtractor)
        simulate(mdp, rl)
        total = 0
        not_zero = 0
        l = []
        for w in rl.weights:
            if rl.weights[w] != 0:
                l.append((-rl.weights[w], w))
                not_zero += 1
            total += 1
        print total
        print not_zero
        l = sorted(l)
        for i in range(10):
            print l[i][1], -l[i][0]

        # Start num_times game.
        rl.explorationProb = 0
        score = 0.0
        for _ in range(num_times):
            # A new game
            player = AIPlayer(self.length, self.width, self.num_mines)
            while not player.gameEnds():
                a = rl.getAction(player.currentPlayerBoard, ProbabilityMine(player))
                if a[0] == "quit":
                    break
                player.move(a[0], a[1], a[2])
            score += player.score
        return score / num_times





