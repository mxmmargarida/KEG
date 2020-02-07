"""
License: MIT

PYTHON 3

Verification of NE for W-KEG
"""
from Graph_Generation import *
from MaximumMatching_Kbest import *
import cplex
# INPUT
# M - list of edges in matching M; each edge is a set
# p - player p for who one wants to verify incentive to deviate
# G - graph
# output
# True = no incentive to deviate
# False = otherwise
def BestResponse_player(G,p,M,info=False):
    k = 1
    # record of solutions: edges selected by player p
    x_sol_past = [e for e in G.Edges_player(p)["int"].keys() if set(e) in M]
    x_execept_p = [e for e in G.EdgesInt() if set(e) in M and e not in x_sol_past]
    aux = True
    LB = G.MatchingValue(p,M)
    m = cplex.Cplex()
    # output stream setup
    m.set_log_stream(None)
    m.set_error_stream(None)
    m.set_warning_stream(None)
    m.set_results_stream(None)
    m.parameters.threads.set(1)
    m.objective.set_sense(m.objective.sense.maximize)
    # variables
    m.variables.add(names = ["x_" + str(e) for e in G.Edges_player(p)["int"].keys()], obj = [G.Edges_player(p)["int"][e] for e in G.Edges_player(p)["int"].keys()], types = ['B' for e in G.Edges_player(p)["int"].keys()])
    m.variables.add(names = ["y_" + str(e) for e in G.EdgesExt(M,p)], obj = [(G.Edges_player(p)["ext"][e] if e in G.Edges_player(p)["ext"].keys() else 0) for e in G.EdgesExt(M,p)], types = ['B' for e in G.EdgesExt(M,p)])
    # matching linear_constraints
    m.linear_constraints.add(names = ["matching const "+str(i) for i in G.V_player(p)], senses = ["L" for i in G.V_player(p)],rhs = [1 for i in G.V_player(p)], lin_expr = [cplex.SparsePair(ind = ["x_"+str(e) for e in G.Edges_player(p)["int"].keys() if i in set(e)]+["y_"+str(e) for e in G.EdgesExt(M,p) if i in set(e)], val = [1 for e in G.Edges_player(p)["int"].keys() if i in set(e)]+[1 for e in G.EdgesExt(M,p) if i in set(e)]) for i in G.V_player(p)])
    for j in range(1,G.Numb()+1):
        if j != p:
            m.linear_constraints.add(names = ["matching const "+str(i) for i in G.V_player(j)], senses = ["L" for i in G.V_player(j)],rhs = [1 for i in G.V_player(j)], lin_expr = [cplex.SparsePair(ind = ["y_"+str(e) for e in G.EdgesExt(M,p) if i in set(e)], val = [1 for e in G.EdgesExt(M,p) if i in set(e)]) for i in G.V_player(j)])
    # no good constraints
    m.linear_constraints.add(names = ["no good "+str(k)], senses = ["G"],rhs = [1-len(x_sol_past)], lin_expr = [cplex.SparsePair(ind = ["x_"+str(e) for e in G.Edges_player(p)["int"].keys() if e not in x_sol_past]+["x_"+str(e) for e in x_sol_past], val = [1 for e in G.Edges_player(p)["int"].keys() if e not in x_sol_past]+[-1 for e in x_sol_past])])
    while aux:
        m.solve()
        if m.solution.get_status() in [101,102]:
            x_sol_past = [e for e in G.Edges_player(p)["int"].keys() if m.solution.get_values("x_"+str(e))>0.9 ]
            UB = m.solution.get_objective_value()
            if UB-10**-9 <= LB:
                return aux # no incentive to deviate
        else: # optimization INFEASIBLE
            if info:
                print("infeasible")
            return aux
        # compute IA solution
        y_sol = IA_decision(G,p,x_sol_past,x_execept_p) # algorithm D.0.2 of the paper
        M_k = [set(e) for e in x_sol_past+y_sol]
        if G.MatchingValue(p,M_k) > LB:
            if info:
                print("best response is: ",x_sol_past, " with IA ",y_sol)
            return False
        k = k+1
        # no good constraints
        m.linear_constraints.add(names = ["no good "+str(k)], senses = ["G"],rhs = [1-len(x_sol_past)], lin_expr = [cplex.SparsePair(ind = ["x_"+str(e) for e in G.Edges_player(p)["int"].keys() if e not in x_sol_past]+["x_"+str(e) for e in x_sol_past], val = [1 for e in G.Edges_player(p)["int"].keys() if e not in x_sol_past]+[-1 for e in x_sol_past])])

def IA_decision(G,p,x_sol_past,x_execept_p):
    M = [{i,j} for i,j in x_sol_past+x_execept_p]
    OPT, _ , _ = OptimalMatching(G, G.EdgesExt(M), [], [])
    mIA = cplex.Cplex()
    # output stream setup
    mIA.set_log_stream(None)
    mIA.set_error_stream(None)
    mIA.set_warning_stream(None)
    mIA.set_results_stream(None)
    mIA.parameters.threads.set(1)
    mIA.objective.set_sense(mIA.objective.sense.minimize)
    # variables
    mIA.variables.add(names = ["y_" + str(e) for e in G.EdgesExt(M)], obj = [G.Edges_player(p)["ext"][e] if e in G.Edges_player(p)["ext"].keys() else 0 for e in G.EdgesExt(M)], types = ['B' for e in G.EdgesExt(M)])
    # matching linear_constraints
    mIA.linear_constraints.add(names = ["matching const "+str(i) for i in G.vertices()], senses = ["L" for i in G.vertices()],rhs = [1 for i in G.vertices()], lin_expr = [cplex.SparsePair(ind = ["y_"+str(e) for e in G.EdgesExt(M) if i in set(e)], val = [1 for e in G.EdgesExt(M) if i in set(e)]) for i in G.vertices()])
    # minimum benefit
    mIA.linear_constraints.add(names = ["minimum benefit "], senses = ["G"],rhs = [OPT-0.00001], lin_expr = [cplex.SparsePair(ind = ["y_"+str(e) for e in G.EdgesExt(M)], val = [G.weight(e)+G.weight((e[1],e[0])) for e in G.EdgesExt(M)])])
    mIA.solve()
    y_sol = [e for e in G.EdgesExt(M) if mIA.solution.get_values("y_"+str(e))>0.9 ]
    return y_sol

# INPUT
# M - matching; list of edges (represented by sets)
# G - graph game
# info = false if no output of results
# OUTPUT
# True - if it is a NE
# False - otherwise
def Verify_NE(M,G, info = False):
    aux = True
    for p in range(1,G.Numb()+1):
        aux = BestResponse_player(G,p,M)
        if not aux:
            if info:
                print("It is not NE")
            return False
    if info:
        print("It is a NE")
    return aux

if __name__ == "__main__":
    G = {1:[2],2:[1,3],3:[2,4],4:[3,5,13],5:[4,6],6:[5,7,10],7:[6,8],8:[7,9],9:[8],10:[6,11],11:[10,12],12:[11],13:[4,14],14:[13,15],15:[14,16],16:[15,17],17:[16]}
    G = Graph(G,None,3)
    G.add_player(1, [1,10])
    G.add_player(2, [2,3,5,7,8,9,11,13,15,16,17])
    G.add_player(3, [4,6,12,14])
    M = [{1,2},{3,4},{5,6},{7,8},{10,11},{13,14},{15,16}]
    print(BestResponse_player(G,2,M))

    print(BestResponse_player(G,1,M))

    print(BestResponse_player(G,3,M))

    G={18:[19],19:[18,20],20:[19]}
    G = Graph(G,None,2)
    G.add_player(1, [18])
    G.add_player(2, [19,20])
    M=[{18,19}]
    print(Verify_NE(M,G))
