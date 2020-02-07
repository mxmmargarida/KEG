"""

License: MIT
PYTHON 3
Computation of the K best maximum weighted matchings.
"""

from Graph_Generation import *

from random import seed, shuffle
# initialize seed
seed(1)

import cplex

# PERMUTATION of vertices indexes
def Permutation_Edges(G):
    set_E = G.edges()
    shuffle(set_E)
    return set_E

# solve maximum weighted matching with variables x_fix fixed
# INPUT
# G - graph with structure from Graph_Generation
# set_E = G.edges() but after random permutation
# x_fix_0 - set of edges fixed to zero
# x_fix_1 - set of edges fixed to one
def OptimalMatching(G, set_E, x_fix_0, x_fix_1):
    # create model
    m = cplex.Cplex()
    # output stream setup
    m.set_log_stream(None)
    m.set_error_stream(None)
    m.set_warning_stream(None)
    m.set_results_stream(None)
    m.parameters.threads.set(1)
    m.objective.set_sense(m.objective.sense.maximize)
    # variables
    set_tuple_E = [tuple(e) for e in set_E]
    m.variables.add(names = ["x_" + str(e) for e in set_E], obj = [G.weight((v1,v2))+G.weight((v2,v1)) for (v1,v2) in set_tuple_E], types = ['B' for e in set_E])
    # fixing constraints
    m.linear_constraints.add(names = ["constraints fix "+str(e) for e in x_fix_0], senses = ["E" for e in x_fix_0],rhs = [0 for e in x_fix_0], lin_expr = [cplex.SparsePair(ind = ["x_"+str(e)], val = [1]) for e in x_fix_0])
    m.linear_constraints.add(names = ["constraints fix "+str(e) for e in x_fix_1], senses = ["E" for e in x_fix_1],rhs = [1 for e in x_fix_1], lin_expr = [cplex.SparsePair(ind = ["x_"+str(e)], val = [1]) for e in x_fix_1])
    # matching constraints
    m.linear_constraints.add(names = ["constraint to "+str(vertex) for vertex in G.vertices()], senses = ["L" for vertex in G.vertices()],rhs = [1.0 for vertex in G.vertices()], lin_expr = [ cplex.SparsePair(ind = ["x_"+str(e) for e in set_E if vertex in e], val = [1 for e in set_E if vertex in e]) for vertex in G.vertices()])
    t_ini = m.get_time()
    m.solve()
    t_fin = m.get_time()
    if m.solution.get_status() in [101,102]:
        x_sol = [e for e in set_E if m.solution.get_values("x_"+str(e))>0.9 ]
        #print("\nThe matching is x_sol: ", x_sol)
        OPT = m.solution.get_objective_value()
        #print("OPT: ", OPT)
        return OPT, x_sol, t_fin-t_ini
    #print("\nINFEASIBLE")
    return 0, [], t_fin-t_ini

def K_best(G, set_E, K):
    n = len(set_E)
    SOL = []
    # STEP 1
    LIST_x,LIST_OPT, LIST_fix = [],[],[]
    k = 1
    OPT, x_OPT, _ = OptimalMatching(G, set_E, [],[])
    LIST_x.append(x_OPT)
    LIST_OPT.append(OPT)
    LIST_fix.append(([],[]))
    aux = LIST_OPT.index(max(LIST_OPT))
    SOL.append((LIST_x[aux],LIST_OPT[aux]))
    x_k = LIST_x[aux][:]
    x_fix_0 = LIST_fix[aux][0] #edges fixed to 0

    x_fix_1 = LIST_fix[aux][1] # edges fixed to 1
    del LIST_x[aux]
    del LIST_OPT[aux]
    del LIST_fix[aux]
    # STEP 2
    while k < K:
        # STEP 3
        # create n-s problems
        s = len(x_fix_0)+len(x_fix_1)
        aux_e = 0
        for i in range(s+1,n+1):
            add_0 = []
            add_1 = []
            add_now_1 = []
            add_now_0 = []
            ########### more efficient than code above commented:
            if set_E[i-1] in x_k:
                add_1.append(set_E[i-1])
                add_now_0.append(set_E[i-1])
            else:
                add_0.append(set_E[i-1])
                add_now_1.append(set_E[i-1])
            ########### end of more efficient
            OPT, x_OPT, _ = OptimalMatching(G, set_E, x_fix_0+add_now_0,x_fix_1+add_now_1)
            if x_OPT != []:
                LIST_x.append(x_OPT)
                LIST_OPT.append(OPT)
                LIST_fix.append(( x_fix_0+add_now_0,x_fix_1+add_now_1))
            x_fix_0 = x_fix_0+add_0
            x_fix_1 = x_fix_1+add_1
        k = k + 1
        # step 1
        if LIST_OPT == []:
            return SOL
        aux = LIST_OPT.index(max(LIST_OPT))
        SOL.append((LIST_x[aux],LIST_OPT[aux]))
        x_k = LIST_x[aux][:]
        x_fix_0 = LIST_fix[aux][0]
        x_fix_1 = LIST_fix[aux][1]
        del LIST_fix[aux]
        del LIST_x[aux]
        del LIST_OPT[aux]
    return SOL







if __name__ == "__main__":
    G = {1: [2, 3, 5], 2: [1], 3: [1], 4: [], 5: [1]}
    G = Graph(G,{(1, 2): 2, (1, 3): 5, (1, 5): 7, (2, 1): 2, (3, 1): 5, (5, 1): 7})
    set_E = Permutation_Edges(G)
    x_fix_0 = []
    x_fix_1 = []
    OPT, x_OPT, t_OPT = OptimalMatching(G, set_E, x_fix_0, x_fix_1)
    K = 1
    SOL = K_best(G, set_E, K)

    # W = {(1, 2): 1,
    # (2, 1): 1,
    #  (2, 3): 1,
    #  (3, 2): 1,
    #  (3, 4): 1,
    #  (4, 3): 1,
    #  (4, 5): 1,
    #  (4, 6): 1,
    #  (4, 7): 1,
    #  (5, 4): 1,
    #  (6, 4): 1,
    #  (7, 4): 1}
    # G = Graph({1:[2],2:[1,3],3:[2,4],4:[3,5,6,7],5:[4],6:[4],7:[4]},W)
    # K = 10
    # #set_E = Permutation_Edges(G)
    # #SOL = K_best(G, set_E, K)
    # SOL = K_best(G, G.edges(), K)
