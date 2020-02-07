"""
License: MIT
PYTHON 3
Generation of graphs
"""

import cplex

class Graph(object):
    def __init__(self, graph_dict = None, weights_dict = None, numb_player = 0):
        if graph_dict == None:
            graph_dict = {}
        if weights_dict == None:
            weights_dict = {}
        self.__graph_dict = graph_dict
        self.__weights_dict = weights_dict
        self.__numb_player = numb_player
        self.__players_V = {i:[] for i in range(0,numb_player+1)}
        self.__players_V_weights = {p:{"int":{},"ext":{}} for p in range(1,numb_player+1)}
        self.__players_name = {p:str(p) for p in range(1,numb_player+1)}

    # random generation of a graph
    def Read_Graph(self,filename):
        if self.__graph_dict == {}: # G = {}
            f = open(filename)
            num_V, num_E = map(int,f.readline().split())
            G_tmp = {}
            for _ in range(num_E):
                v1, v2, w = map(int,f.readline().split())
                if v2 not in G_tmp:
                    G_tmp[v2] = []
                if v1 in G_tmp:
                    G_tmp[v1].append(v2)
                else:
                    G_tmp[v1] = [v2]
            # next: identify cycles of length 2
            self.__graph_dict = {v1:[] for v1 in G_tmp.keys()}
            for v1 in G_tmp.keys():
                for v2 in G_tmp[v1]:
                    if v1 in G_tmp[v2]:
                        self.add_edge((v1,v2))


    # number of players
    def Numb(self):
        return self.__numb_player

    # set of vertices of player p
    def V_player(self, player):
        return self.__players_V[player]

    def Edges_player(self,player):
        return self.__players_V_weights[player]

    # V_player is a list of vertices
    # weights_player is a dictionary of edges
    def add_player(self, player, V_player, weights_player = None, name = None):
        self.__players_V[player] = V_player
        if name != None:
            self.__players_name[player] = name
        if weights_player == None:
            self.__players_V_weights[player]["int"] = {(i,j):2 for (i,j) in self.edges() if i in self.__players_V[player] and j in self.__players_V[player]}
            self.__players_V_weights[player]["ext"] = {(i,j):1 for (i,j) in self.edges() if (i in self.__players_V[player] and j not in self.__players_V[player]) or (i not in self.__players_V[player] and j in self.__players_V[player])}
        else:
            self.__players_V_weights[player]["int"] = weights_player["int"]
            self.__players_V_weights[player]["ext"] = weights_player["ext"]

    def get_name_player(self,player):
        return self.__players_name[player]

    def vertices(self, player = None):
        # return vertices of a graph
        if player == None:
            return list(self.__graph_dict.keys())


    def edges(self):
        # return edges of a graph
        return self.__generate_edges()

    # external edges available except player p
    def EdgesExt(self, M = [], player = 0):
        interdicted = set()
        for (i,j) in self.EdgesInt():
            if {i,j} in M and i not in self.V_player(player):
                interdicted.add(i)
                interdicted.add(j)
        edgesext = []
        for p in range(1, self.Numb() +1):
            for (i,j) in self.Edges_player(p)["ext"]:
                if (i,j) not in edgesext and i not in interdicted and j not in interdicted:
                    edgesext.append((i,j))
        return edgesext

    # internal edges
    def EdgesInt(self):
        edgesint = []
        for p in range(1, self.Numb() +1):
            for e in self.Edges_player(p)["int"]:
                if e not in edgesint:
                    edgesint.append(e)
        return edgesint


    def weights(self):
        return self.__generate_weights()

    # edge must be a list or tuple because order matters for weights
    def weight(self, edge):
        return self.weights()[tuple(edge)]

    def neighbour(self,vertex):
        if vertex not in self.__graph_dict:
            return []
        return self.__graph_dict[vertex]

    def add_vertex(self,vertex):
        if vertex not in self.__graph_dict:
            self.__graph_dict[vertex] = []

    def add_edge(self,edge,weigt_edge=[1,1]):
        (vertex1,vertex2) = tuple(edge)
        edge = set(edge)
        if edge not in self.edges():
            self.__weights_dict[(vertex1,vertex2)] = weigt_edge[0]
            self.__weights_dict[(vertex2,vertex1)] = weigt_edge[1]
            if vertex1 in self.__graph_dict:
                self.__graph_dict[vertex1].append(vertex2)
            else:
                self.__graph_dict[vertex1] = [vertex2]
            if vertex2 in self.__graph_dict:
                self.__graph_dict[vertex2].append(vertex1)
            else:
                self.__graph_dict[vertex2] = [vertex1]
            # add edges to the players
            for p in range(1,self.Numb()+1):
                if vertex1 in self.__players_V[p]:
                    if vertex2 in self.__players_V[p]:
                        self.__players_V_weights[p]["int"][(vertex1,vertex2)] = weigt_edge[0]+weigt_edge[1]
                    else:
                        # benefit for vertex1 of receiving from vertex 2
                        self.__players_V_weights[p]["ext"][(vertex1,vertex2)] = weigt_edge[1]
                        for p2 in range(1,self.Numb()+1):
                            if vertex2 in self.__players_V[p2]:
                                self.__players_V_weights[p2]["ext"][(vertex1,vertex2)] = weigt_edge[0]


    def __generate_edges(self):
        edges = []
        for vertex in self.__graph_dict:
            for neighbour in self.__graph_dict[vertex]:
                if {neighbour,vertex} not in edges:
                    edges.append({vertex,neighbour})
        return edges

    def __generate_weights(self):
        weights =  self.__weights_dict
        if weights == {}:
            for (vertex,neighbour) in self.edges():
                weights[(vertex,neighbour)] = 1
                weights[(neighbour,vertex)] = 1
        return weights

    def MatchingValue(self,p,M):
        return sum(self.Edges_player(p)["int"][e] for e in self.Edges_player(p)["int"].keys() if set(e) in M) + sum(self.Edges_player(p)["ext"][e] for e in self.Edges_player(p)["ext"].keys() if set(e) in M)

    ## player profit alone
    def ProfitAlone(self,p):
        m = cplex.Cplex()
        # output stream setup
        m.set_log_stream(None)
        m.set_error_stream(None)
        m.set_warning_stream(None)
        m.set_results_stream(None)
        m.parameters.threads.set(1)
        # maximize
        m.objective.set_sense(m.objective.sense.maximize)
        m.variables.add(names = ["xp_" + str(e) for e in self.Edges_player(p)["int"].keys()], obj = [self.Edges_player(p)["int"][e] for e in self.Edges_player(p)["int"].keys()], types = ['B' for e in self.Edges_player(p)["int"].keys()])
        m.linear_constraints.add(names = ["matching const "+str(i) for i in self.V_player(p)], senses = ["L" for i in self.V_player(p)],rhs = [1 for i in self.V_player(p)], lin_expr = [cplex.SparsePair(ind = ["xp_"+str(e) for e in self.Edges_player(p)["int"].keys() if i in set(e)], val = [1 for e in self.Edges_player(p)["int"].keys() if i in set(e)]) for i in self.V_player(p)])
        m.solve()
        #xp_sol = [e for e in self.Edges_player(p)["int"].keys() if m.solution.get_values("xp_"+str(e))>0.9]
        return m.solution.get_objective_value()


    # print graph together with matching M=[{1,2},{3,2},..]
    # avail_colors = ["#767ecc","#cc757d","#74cc93"]
    def print_game(self,avail_colors = ['#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080', '#ffffff', '#000000'],M=[]):
        #from pydot import *
        import os
        if os.name =='nt':
            os.environ["PATH"] += os.pathsep + 'C:/Program Files (x86)/Graphviz2.38/bin/'
        import pydot
        graph = pydot.Dot(graph_type='graph')
        Nodes_V = {}

        #avail_colors = ["#767ecc","#cc757d","#74cc93"]

        #avail_colors = colors(n)
        for i in self.vertices():
            # if there are players
            for p in range(1,self.Numb()+1): # set of players
                if i in self.V_player(p):
                    color_p = avail_colors[(p-1)%len(avail_colors)]
                    Nodes_V[i] = pydot.Node(str(i), shape="square",style="filled", fillcolor = color_p)
                    break
            ########## if no players
            if self.Numb() == 0:
                Nodes_V[i] = pydot.Node(str(i), shape="square",style="filled", fillcolor = "#767ecc")
            #ok, now we add the node to the graph
            graph.add_node(Nodes_V[i])
        temporario = set({})
        for (i,j) in self.edges():
            if {i,j} in M:
                edge = pydot.Edge(Nodes_V[i], Nodes_V[j], label="M", color="#6cef1a")
            else:
                edge = pydot.Edge(Nodes_V[i], Nodes_V[j])
            graph.add_edge(edge)
            temporario.add((j,i))
        graph.write_png('graphGame.png')
        return None

    def __str__(self):
        res = "vertices: "
        for k in self.__graph_dict:
            res += str(k) + " "
        res += "\nedges: "
        for edge in self.__generate_edges():
            res += str(edge) + " "+ "w=" + str(self.weight(edge)) +" "
        res += "\nnumber of players: " + str(self.Numb()) + "\n"
        for player in range(1,self.Numb()+1):
            res += "Player: "+self.__players_name[player] +" vertices " +str(self.__players_V[player])
            res += "        edges: "+str(self.__players_V_weights[player])+"\n"
        return res






#if __name__ == "__main__":
    ## MANUAL GENERATION OF A GRAPH
    # G = {1: [2, 3, 5], 2: [1], 3: [1], 4: [], 5: [1]}
    # G = Graph(G)
    # #print(G)
    # G.neighbour(1)
    #
    # G = {1: [2, 3, 4, 5], 2: [1], 3: [1], 4: [6, 1], 5: [1],6:[4]}
    # G = Graph(G,None,3)
    # G.add_player(1, [3])
    # G.add_player(2, [1])
    # G.add_player(3, [2,4,5,6])
    #
    # G = {1:[2],2:[1,3],3:[2,4],4:[3,5,13],5:[4,6],6:[5,7,10],7:[6,8],8:[7,9],9:[8],10:[6,11],11:[10,12],12:[11],13:[4,14],14:[13,15],15:[14,16],16:[15,17],17:[16]}
    # G = Graph(G,None,3)
    # G.add_player(1, [1,10])
    # G.add_player(2, [2,3,5,7,8,9,11,13,15,16,17])
    # G.add_player(3, [4,6,12,14])
