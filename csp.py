import collections, util, copy
import random
from Player import AIPlayer

# A backtracking algorithm that solves weighted CSP.
# Usage:
#   search = BacktrackingSearch()
#   search.solve(csp)
class BacktrackingSearch():

    def reset_results(self):
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments = []
        self.max_assignment = collections.defaultdict(int)

    def print_stats(self):
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print "Found %d optimal assignments with weight %f in %d operations" % \
                (self.numOptimalAssignments, self.optimalWeight, self.numOperations)
            print "First assignment took %d operations" % self.firstAssignmentNumOperations
        else:
            print "No solution was found."

    def get_delta_weight(self, assignment, var, val):
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return w
        for var2, factor in self.csp.binaryFactors[var].iteritems():
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0: return w
        return w

    def solve(self, csp, mcv = False, ac3 = False):
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that unlike a typical unweighted CSP where the search
        terminates when one solution is found, we want this function to find
        all possible assignments. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp

        # Set the search heuristics requested asked.
        self.mcv = mcv
        self.ac3 = ac3

        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

        # Perform backtracking search.
        self.backtrack({}, 0, 1)
        # Print summary of solutions.
        # self.print_stats()

    def backtrack(self, assignment, numAssigned, weight):
        """
        Perform the back-tracking algorithms to find all possible solutions to
        the CSP.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param numAssigned: Number of currently assigned variables
        @param weight: The weight of the current partial assignment.
        """

        self.numOperations += 1
        assert weight > 0
        if numAssigned == self.csp.numVars:
            # A satisfiable solution have been found. Update the statistics.
            self.numAssignments += 1
            newAssignment = {}
            for var in self.csp.variables:
                self.max_assignment[(var, assignment[var])] += 1
                newAssignment[var] = assignment[var]
            self.allAssignments.append(newAssignment)

            if len(self.optimalAssignment) == 0 or weight >= self.optimalWeight:
                if weight == self.optimalWeight:
                    self.numOptimalAssignments += 1
                else:
                    self.numOptimalAssignments = 1
                self.optimalWeight = weight

                self.optimalAssignment = newAssignment
                if self.firstAssignmentNumOperations == 0:
                    self.firstAssignmentNumOperations = self.numOperations
            return

        # Select the next variable to be assigned.
        var = self.get_unassigned_variable(assignment)
        # Get an ordering of the values.
        ordered_values = self.domains[var]

        # Continue the backtracking recursion using |var| and |ordered_values|.
        if not self.ac3:
            # When arc consistency check is not enabled.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    del assignment[var]
        else:
            # Arc consistency check is enabled.
            # Problem 1c: skeleton code for AC-3
            # You need to implement arc_consistency_check().
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    # create a deep copy of domains as we are going to look
                    # ahead and change domain values
                    localCopy = copy.deepcopy(self.domains)
                    # fix value for the selected variable so that hopefully we
                    # can eliminate values for other variables
                    self.domains[var] = [val]

                    # enforce arc consistency
                    self.arc_consistency_check(var)

                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    # restore the previous domains
                    self.domains = localCopy
                    del assignment[var]

    def get_unassigned_variable(self, assignment):
        """
        Given a partial assignment, return a currently unassigned variable.

        @param assignment: A dictionary of current assignment. This is the same as
            what you've seen so far.

        @return var: a currently unassigned variable.
        """

        if not self.mcv:
            # Select a variable without any heuristics.
            for var in self.csp.variables:
                if var not in assignment: return var
        else:
            # Problem 1b
            # Heuristic: most constrained variable (MCV)
            # Select a variable with the least number of remaining domain values.
            # Hint: given var, self.domains[var] gives you all the possible values
            # Hint: get_delta_weight gives the change in weights given a partial
            #       assignment, a variable, and a proposed value to this variable
            # Hint: for ties, choose the variable with lowest index in self.csp.variables
            # BEGIN_YOUR_CODE (our solution is 7 lines of code, but don't worry if you deviate from this)
            min_num_valid_choices = float('inf')
            result = None
            for var in self.csp.variables:
                if var not in assignment:
                        l = [self.get_delta_weight(assignment, var, possible_value) for possible_value in self.domains[var]]
                        num_valid_choices = [i for i in l if i != 0]
                        if len(num_valid_choices) < min_num_valid_choices:
                            min_num_valid_choices = len(num_valid_choices)
                            result = var
            return result


            # END_YOUR_CODE

    def arc_consistency_check(self, var):
        """
        Perform the AC-3 algorithm. The goal is to reduce the size of the
        domain values for the unassigned variables based on arc consistency.

        @param var: The variable whose value has just been set.
        """
        # Problem 1c
        # Hint: How to get variables neighboring variable |var|?
        # => for var2 in self.csp.get_neighbor_vars(var):
        #       # use var2
        #
        # Hint: How to check if a value or two values are inconsistent?
        # - For unary factors
        #   => self.csp.unaryFactors[var1][val1] == 0
        #
        # - For binary factors
        #   => self.csp.binaryFactors[var1][var2][val1][val2] == 0
        #   (self.csp.binaryFactors[var1][var2] returns a nested dict of all assignments)

        # BEGIN_YOUR_CODE (our solution is 20 lines of code, but don't worry if you deviate from this)
        q = collections.deque([var])
        while len(q) > 0:
            v = q.popleft()
            for var2 in self.csp.get_neighbor_vars(v):
                v2_list = self.domains[var2][:]
                for val2 in self.domains[var2]:
                    all_values = [self.csp.binaryFactors[v][var2][val1][val2] for val1 in self.domains[v]]
                    non_zero_values = [i for i in all_values if i != 0]
                    if len(non_zero_values) == 0:
                        v2_list.remove(val2)
                if self.domains[var2] != v2_list:
                    q.append(var2)
                self.domains[var2] = v2_list
        # END_YOUR_CODE

def get_sum_variable(csp, name, variables, maxSum):
    """
    Given a list of |variables| each with non-negative integer domains,
    returns the name of a new variable with domain range(0, maxSum+1), such that
    it's consistent with the value |n| iff the assignments for |variables|
    sums to |n|.

    @param name: Prefix of all the variables that are going to be added.
        Can be any hashable objects. For every variable |var| added in this
        function, it's recommended to use a naming strategy such as
        ('sum', |name|, |var|) to avoid conflicts with other variable names.
    @param variables: A list of variables that are already in the CSP that
        have non-negative integer values as its domain.
    @param maxSum: An integer indicating the maximum sum value allowed. You
        can use it to get the auxiliary variables' domain

    @return result: The name of a newly created variable with domain range
        [0, maxSum] such that it's consistent with an assignment of |n|
        iff the assignment of |variables| sums to |n|.
    """
    # BEGIN_YOUR_CODE (our solution is 18 lines of code, but don't worry if you deviate from this)
    result = ('sum', name, len(variables))
    csp.add_variable(result, range(maxSum + 1))
    if len(variables) == 0:
        csp.add_unary_factor(result, lambda val: val == 0)
        return result
    for i, X_i in enumerate(variables):
        A_i = ('sum', name, i)
        csp.add_variable(A_i, [(x, y) for x in range(maxSum + 1) for y in range(maxSum + 1)])
        csp.add_binary_factor(X_i, A_i, lambda val, b: b[1] == b[0] + val)
        if i == 0:
            csp.add_unary_factor(A_i, lambda b: b[0] == 0)
        else:
            csp.add_binary_factor(('sum', name, i - 1), A_i, lambda b1, b2: b1[1] == b2[0])
    csp.add_binary_factor(A_i, result, lambda val, res: val[1] == res)
    return result
    # END_YOUR_CODE

class CspAIPlayer(AIPlayer):
    def run(self, save_log=False):
        csp = util.CSP()
        # First action is always (0,0).
        chance_flag = float(self.num_mines) / (self.length * self.width)
        a = ("flag", 0, 0) if random.random() < chance_flag else ("click", 0, 0) 
        added_variables = {(0, 0): 1}
        self.move(a[0], a[1], a[2])
        csp.add_variable((0, 0), [0, 1])
        just_started = True
        sum_added = False
        while not self.gameEnds():
            revealed_tile = self.currentPlayerBoard[a[1]][a[2]]
            csp.values[(a[1], a[2])] = [0] if revealed_tile >= 0 else [1]
            if revealed_tile != -1:
                just_started = False
                list_surrounding_tiles = [(x1, y1) for x1 in range(a[1] - 1, a[1] + 2) if x1 >= 0 and x1 < self.length for y1 in range(a[2] - 1, a[2] + 2) if y1 >= 0 and y1 < self.width]
                for x in list_surrounding_tiles:
                    if x not in added_variables:
                        csp.add_variable(x, [0, 1])
                        added_variables[x] = 1
                sumVar = get_sum_variable(csp, "sum:(" + str(a[1]) + "," + str(a[2]) + ")", list_surrounding_tiles, revealed_tile)
            elif just_started:
                a = self.chooseAction(a[1], a[2])
                self.move(a[0], a[1], a[2])
                continue
            if len(added_variables) == self.length * self.width and not sum_added:
                sumVar = get_sum_variable(csp, "totalSum", list(added_variables.keys()), self.num_mines)
                sum_added = True
            solver = BacktrackingSearch()
            solver.solve(csp, True, True)
            pos, value = self.findMostOccurredPos(solver)
            if value == 0:
                a = ("click", pos[0], pos[1])
            else:
                a = ("flag", pos[0], pos[1])
            self.move(a[0], a[1], a[2])
        if save_log:
            self.save('csp')
        return self.score, self.correct_moves, self.correct_mines

    def findMostOccurredPos(self, solver):
        # First remove all the sum variables.
        d = copy.deepcopy(solver.max_assignment)
        for k in solver.max_assignment.keys():
            if type(k[0][0]) != int or type(k[0][1]) != int:
                del d[k]
            elif self.currentPlayerBoard[k[0][0]][k[0][1]] != 'x':
                del d[k]
        maxOccurred = d[max(d, key=d.get)]
        maxL = []
        for k in d.keys():
            if d[k] == maxOccurred:
                maxL.append(k)
        return random.choice(maxL)









