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

    def solve(self, csp, changed_var_list, mcv = False, ac3 = False):
        self.csp = csp
        self.mcv = mcv
        self.ac3 = ac3
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}
        self.max_assignment = collections.defaultdict(int)

        # Perform backtracking search.
        if len(self.allAssignments) > 0:
            assignments_copy = self.allAssignments[:]
            self.allAssignments = []
            for assignment in assignments_copy:
                if self.checkAssignment(assignment, changed_var_list):
                    self.backtrack(assignment, len(assignment), 1)
        else:
            self.backtrack({}, 0, 1)
        # Print summary of solutions.
        self.print_stats()

    def checkAssignment(self, assignment, changed_var_list):
        for var in changed_var_list:
            if var not in assignment:
                continue
            if assignment[var] not in self.domains[var]:
                return False
        return True

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
        # if len(self.allAssignments) > 10:
        #     print "we already have a lot of assignments"
        #     return

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
        if not self.mcv:
            for var in self.csp.variables:
                if var not in assignment: return var
        else:
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

    def arc_consistency_check(self, var):
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

def get_sum_variable(csp, name, variables, maxSum):
    for i, X_i in enumerate(variables):
        A_i = ('sum', name, i)
        csp.add_variable(A_i, [(x, y) for x in range(maxSum + 1) for y in range(maxSum + 1)])
        csp.add_binary_factor(X_i, A_i, lambda val, b: b[1] == b[0] + val)
        if i == 0:
            csp.add_unary_factor(A_i, lambda b: b[0] == 0)
        else:
            csp.add_binary_factor(('sum', name, i - 1), A_i, lambda b1, b2: b1[1] == b2[0])
    csp.add_unary_factor(A_i, lambda val: val[1] == maxSum)

class CspAIPlayer(AIPlayer):
    def run(self, save_log=True):
        print self.seed
        csp = util.CSP()
        solver = BacktrackingSearch()
        # First action is always (0,0).
        chance_flag = float(self.num_mines) / (self.length * self.width)
        a = ("flag", 0, 0) if random.random() < chance_flag else ("click", 0, 0)
        self.num_flags_remaining = self.length * self.width
        added_variables = {(0, 0): 1}
        self.move(a[0], a[1], a[2])
        csp.add_variable((0, 0), [0, 1])
        sum_added = False
        list_changed_var = []
        known_tiles_to_explore = {}
        while not self.gameEnds():
            # print a
            # self.printPlayerBoard()
            revealed_tile = self.currentPlayerBoard[a[1]][a[2]]
            csp.values[(a[1], a[2])] = [0] if revealed_tile >= 0 else [1]
            list_changed_var.append((a[1], a[2]))
            # print "revealed tile is: " + str(revealed_tile)
            list_surrounding_tiles = [(x1, y1) for x1 in range(a[1] - 1, a[1] + 2) if x1 >= 0 and x1 < self.length for y1 in range(a[2] - 1, a[2] + 2) if y1 >= 0 and y1 < self.width]
            for x in list_surrounding_tiles:
                if x not in added_variables:
                    csp.add_variable(x, [0, 1])
                    added_variables[x] = 1
            if revealed_tile != -1:
                get_sum_variable(csp, "sum:(" + str(a[1]) + "," + str(a[2]) + ")", list_surrounding_tiles, revealed_tile)
            if len(added_variables) == self.length * self.width and not sum_added:
                get_sum_variable(csp, "totalSum", list(added_variables.keys()), self.num_mines)
                sum_added = True
            if len(known_tiles_to_explore) == 0:
                solver.solve(csp, list_changed_var, False, True)
                list_changed_var = []
                for pos, value in self.findMostOccurredPos(solver):
                    if pos not in known_tiles_to_explore:
                        known_tiles_to_explore[pos] = value
            else:
                print "NOT calling solver - saves time ;)"
            pos = known_tiles_to_explore.keys()[0]
            value = known_tiles_to_explore.pop(pos)
            if value == 0:
                a = ("click", pos[0], pos[1])
            else:
                a = ("flag", pos[0], pos[1])
            self.move(a[0], a[1], a[2])
        if save_log:
            self.save('csp')
        return self.score, self.correct_moves, self.correct_mines

    def findMostOccurredPos(self, solver):
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
        return maxL
