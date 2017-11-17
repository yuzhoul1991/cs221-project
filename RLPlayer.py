import math, random
from collections import defaultdict
from Player import AIPlayer

# Performs Q-learning.
# actions: a function that takes a state and returns a list of actions.
# discount: a number between 0 and 1, which determines the discount factor
# featureExtractor: a function that takes a state and action and returns a list of (feature name, feature value) pairs.
# explorationProb: the epsilon value indicating how frequently the policy returns a random action
class QLearningAlgorithm:
    def __init__(self, actions, discount, featureExtractor, explorationProb=0.95):
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
    def getAction(self, state):
        self.numIters += 1
        if random.random() < self.explorationProb:
            return random.choice(self.actions(state))
        else:
            l = [(self.getQ(state, action), action) for action in self.actions(state)]
            if state.num_flags_remaining > 0:
                l = [i for i in l if i[1][0] != "flag"]
            max_weight = max(l)[0]
            # choose random actions based on density of remaining mines.
            click_choices = [i for i in l if i[0] == max_weight and i[1][0] == "click"]
            flag_choices = [i for i in l if i[0] == max_weight and i[1][0] == "flag"]
            if len(click_choices) == 0:
                return random.choice(flag_choices)[1]
            elif len(flag_choices) == 0:
                return random.choice(click_choices)[1]
            numRemainingMines = state.num_mines - len(state.currentMines)
            numRemainingCells = state.length * state.width - state.num_moves
            if state.num_flags_remaining > 0 and random.random() < float(numRemainingMines) / numRemainingCells:
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

# Naive FeatureExtractor. The feature is the current Player board + action.
# Does not perform well at all.
def identityFeatureExtractor(state, action):
    # First serialize state to a string, so that it's hashable:
    string_state = ''.join([''.join(str(e) for e in i) for i in state.currentPlayerBoard])
    featureKey = (string_state, action)
    featureValue = 1
    return [(featureKey, featureValue)]

# Improved FeatureExtractor. Work in progress.
def ImprovedFeatureExtractor(state, action):
    # Focus should be on action - how does this action fit in current state?
    feature_value_list = defaultdict(int)
    # 1st feature: Indicator of (number of mines in state + action - flag or click).
    # feature_key = "Total Mines: " + str(len(state.currentMines)) + " Num Moves: " + str(state.num_moves) + " Action: " + action[0]
    # feature_value_list[feature_key] = state.num_moves
    # 2nd feature: Take a look around the neighbors of the action cell.
    # record 1. distribution of their numbers; 2. Number of unknown tiles; 3. Maximum number.
    list_surrounding_tiles = [(x1, y1) for x1 in range(action[1] - 1, action[1] + 2) if x1 >= 0 and x1 < state.length for y1 in range(action[2] - 1, action[2] + 2) if y1 >= 0 and y1 < state.width]
    max_neighbor_tile, num_max_neighbor_tile = -1, 0
    num_surrounding_mines, num_unknown_mines = 0, 0
    for x, y in list_surrounding_tiles:
        if state.currentPlayerBoard[x][y] != "x" and state.currentPlayerBoard[x][y] >= 0:
            if state.currentPlayerBoard[x][y] > max_neighbor_tile:
                max_neighbor_tile, num_max_neighbor_tile = state.currentPlayerBoard[x][y], 1
            elif state.currentPlayerBoard[x][y] == max_neighbor_tile:
                num_max_neighbor_tile += 1
            feature_key = "Surrounding number: " + str(state.currentPlayerBoard[x][y]) + ";action:" + action[0]
            feature_value_list[feature_key] += 1
        elif state.currentPlayerBoard[x][y] == "x":
            num_unknown_mines += 1
        elif state.currentPlayerBoard[x][y] != "x" and state.currentPlayerBoard[x][y] < 0:
            num_surrounding_mines += 1
    if num_max_neighbor_tile > 0:
        feature_key = "Maximum Surrounding Neighbor: " + str(max_neighbor_tile) + ";action:" + action[0]
        feature_value_list[feature_key] = 1
    # feature_key = "Num Unknown tiles: "
    # feature_value_list[feature_key] = float(num_unknown_mines) / (state.num_moves + 1)
    feature_key = "Num surrounding mines: " + str(num_surrounding_mines) + ";action:" + action[0]
    feature_value_list[feature_key] = 1
    # More features to come!
    return feature_value_list.items()

# State is the current player.
class MiningMDP:
    def __init__(self, length, width, num_mines):
        self.length = length
        self.width = width
        self.num_mines = num_mines

    # Each time we start a new state, we will create a new game.
    def startState(self):
        self.player = AIPlayer(self.length, self.width, self.num_mines)
        return self.player

    def actions(self, state):
        result = []
        for x in range(state.length):
            for y in range(state.width):
                if state.currentPlayerBoard[x][y] == "x":
                    result.append(("click", x, y))
                    if state.num_flags_remaining > 0:
                        result.append(("flag", x, y))
        return result

    # Unlike homework, this will only have a deterministic successor.
    # Returns successor and the reward.
    def succAndProbReward(self, state, action):
        score = self.player.move(action[0], action[1], action[2])
        if self.player.gameEnds():
            return None, None
        return self.player, score

    def discount(self):
        return 0.9

def simulate(mdp, rl, numTrials):
    for trial in range(numTrials):
        if trial % 100 == 0:
            print trial
        state = mdp.startState()
        totalDiscount = 1
        while True:
            action = rl.getAction(state)
            newState, reward = mdp.succAndProbReward(state, action)
            if newState == None:
                rl.incorporateFeedback(state, action, 0, None)
                break
            # Choose a random transition
            rl.incorporateFeedback(state, action, reward, newState)
            totalDiscount *= mdp.discount()
            state = newState


class RLPlayer(AIPlayer):
    def run(self, num_times, episodes=10000):
        # It will first train itself.
        mdp = MiningMDP(self.length, self.width, self.num_mines)
        rl = QLearningAlgorithm(mdp.actions, mdp.discount(), ImprovedFeatureExtractor)
        simulate(mdp, rl, numTrials=episodes)
        # Some printing, to know if the weight makes sense.
        weights = defaultdict(list)
        for f in rl.weights:
            if rl.weights[f] != 0:
                weight = rl.weights[f]
                if ";" in f:
                    feature, action = f.split(";")
                    weights[feature].append((action, weight))
                else:
                    weights[f] = [weight]

        for feature in weights:
            l = weights[feature]
            if len(l) > 1:
                l = sorted(l, key=lambda i: -i[1])
                print feature, l[0], l[1]
            else:
                print feature, l[0]

        # Start num_times game.
        rl.explorationProb = 0
        score = 0.0
        for _ in range(num_times):
            # A new game
            player = AIPlayer(self.length, self.width, self.num_mines)
            # print "NEW GAME"
            while not player.gameEnds():
                a = rl.getAction(player)
                # print a
                if a[0] == "quit":
                    break
                player.move(a[0], a[1], a[2])
            score += player.score
        return score / num_times





