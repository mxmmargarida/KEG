"""
License: MIT
Python 3
Run cardinality test
"""

# # verify NE
import VerifyNE
#
# # copy files
import shutil
#
import time

import os

import os.path

from Graph_Generation import *

# convert graph to a file so that julia can read it
def Write_file(G,instance_name= " "):
    f = open("Graph_file","w")
    f.write(str(len(G.vertices()))+ "  " + str(2*len(G.edges()))+"\n")
    for e in G.edges():
        v = [u for u in e]
        f.write(str(v[0])+" "+str(v[1])+" "+str(1)+"\n")
        f.write(str(v[1])+" "+str(v[0])+" "+str(1)+"\n")
    f.write(str(-1)+" "+str(-1)+" "+str(-1)+"\n")
    f.close()
    if instance_name != " ":
        # copy
        shutil.copyfile('Graph_file', 'Instances/Graph_'+instance_name)
    # no need to save players vertices as they are saved by order of the provinces
    return None



def Read_instance_test(Numb_V,high_sensitized=2009,ins=0):
    name_ins = str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)
    f = open('Instances/Graph_'+name_ins+"_players",'r')
    size_V = eval(f.readline())
    f.close()

    # read graph instance
    G = Graph({},None,len(size_V.keys()))
    f = open('Instances/Graph_'+name_ins,'r')
    _,add_E = map(int,f.readline().split())
    aux_v = 1
    for aux_prov,prov in enumerate(size_V.keys()):
        prov_v = []
        for _ in range(size_V[prov]):
            G.add_vertex(aux_v)
            prov_v.append(aux_v)
            aux_v = aux_v +1
        G.add_player(aux_prov+1, prov_v,None,prov)

    # add edges
    checked_edges = []
    for _ in range(add_E):
        v1, v2, w = map(int,f.readline().split())
        if {v1,v2} in checked_edges and v1!=v2:
            G.add_edge([v1,v2])
        else:
            checked_edges.append({v1,v2})
    f.close()
    return G, size_V


# input
# Numbe_v - total number of vertices
# name_ins - name of the instance
# K - number of matchings to be generated
# OUTPUT
# save statistical results
def Run_Cardinality_instance(Numb_V,K,high_sensitized=2009,ins=0):
    name_ins = str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)


    # STEP 1: read instance
    G, size_V = Read_instance_test(Numb_V,high_sensitized,ins)

    # step 1.1: save instance
    Write_file(G,name_ins)

    # save vertices
    fres = open("results.txt","w")
    # save number of edges
    fres.write("V = "+ str(Numb_V)+"\n")
    fres.write("E = "+ str(len(G.edges()))+"\n")
    for p,prov in enumerate(size_V.keys()):
        fres.write(prov+" V= "+ str(size_V[prov])+"\n")
        fres.write(prov+" E= "+ str(len(G.Edges_player(p+1)["int"]))+"\n")
        ### alone utility
        fres.write("alone "+prov+" ="+str(G.ProfitAlone(p+1))+"\n")
    fres.close()
    # end saving

    # STEP 2: Generate K random matchings
    f=open("size","w")
    f.write(str(K))
    f.close()

    try:
        # it takes time because of pre compilation
        os.system("julia UniformGen_Python_to_Julia.jl")

        print("Julia did its part")

        #  STEP 3 : verify if it is a Nash equilibrium of the cardinality game
        # read file of matchings generated
        f = open("tmp.txt",'r')
        # count Nash equilibria
        count_NE = 0
        # lowest and highest number of international exchanges among computed NE
        low_International = Numb_V
        high_International = 0
        # players payoff statistics
        low_players = {prov: Numb_V for prov in size_V.keys()}
        high_players = {prov: 0 for prov in size_V.keys()}
        t_ini = time.time()
        for _ in range(K):
            gen_M = eval(f.readline())
            if VerifyNE.Verify_NE(gen_M,G):
                count_NE = count_NE + 1
                # save players utilities and M
                # save worst and best M for each player
                for i,prov in enumerate(size_V.keys()):
                    if G.MatchingValue(i+1,gen_M)>high_players[prov]:
                        high_players[prov] = G.MatchingValue(i+1,gen_M)
                    if G.MatchingValue(i+1,gen_M)<low_players[prov]:
                        low_players[prov] = G.MatchingValue(i+1,gen_M)
                # save international RESULTS
                IA_match = sum([2 for e in G.EdgesExt() if set(e) in gen_M])
                if IA_match> high_International:
                    high_International = IA_match
                if IA_match< low_International:
                    low_International = IA_match
                # end saving results
        f.close()
        t_final = (time.time()-t_ini)/K

        # eliminate tmp.txt
        os.remove("tmp.txt")

        # save NE results
        fres = open("results.txt","a")
        fres.write("time for Verify all NE = %.2f \n"%(t_final))
        fres.write("Numb_NE = "+ str(count_NE)+"\n")
        for prov in size_V.keys():
            fres.write("high util "+prov+"= "+ str(high_players[prov])+"\n")
            fres.write("low util "+prov+"= "+ str(low_players[prov])+"\n")
        fres.write("high IA = "+ str(high_International)+"\n")
        fres.write("low IA = "+ str(low_International)+"\n")
        fres.close()
        # end of saving results
        print("Done for instance "+name_ins)
    except:
        print("Something failed during tests")
    shutil.copyfile('results.txt', 'Results/results_'+name_ins+'.txt')
    return G


# statistics part
# input
# K = number of samples of optimal social welfare outcomes (matchings of maximum cardinality)
# optional: remove_prov: provinces not to be considered
def Stats_Part(K,remove_prov=[]):
    prov_names = ['British Columbia & Yukon', 'Alberta', 'Saskatchewan', 'Manitoba', 'Ontario', 'Quebec', 'Nova Scotia', 'New Brunswick', 'Prince Edward Island', 'Newfoundland and Labrador']
    selected_names = [j for j in prov_names if j not in remove_prov]
    # short name
    short = {'British Columbia & Yukon': 'BCYT ', 'Alberta': 'AB', 'Saskatchewan':"SK", 'Manitoba':"MB", 'Ontario':"ON", 'Quebec':"QC", 'Nova Scotia':"NS", 'New Brunswick':"NB", 'Prince Edward Island':"PE", 'Newfoundland and Labrador':"NL"}
    f = open("Results/table_cardinaliy.txt",'w')
    for Numb_V in [30,40,50]:
        for high_sensitized in [2009,2013]:
            for ins in range(21,31):
                # [alone, low, high]
                province_scenarios = {j:[1,1,1] for j in prov_names}
                if os.path.isfile('Results/results_'+str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)+'.txt'):
                    run_all = False # did not terminated all computations
                    tl_gen = False # not enough time to generate
                    with open('Results/results_'+str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)+'.txt', 'r') as fresults:
                        for line in fresults:
                            if line.split("=")[0] == 'E ':
                                E = eval(line.split("=")[1])
                            if line.split("=")[0] == 'maxCard':
                                maxCard = eval(line.split("=")[1])
                            if line.split("=")[0] == 'Numb_NE ':
                                per_NE = 100*((eval(line.split("=")[1])*1.)/K)
                            if line.split("=")[0]== 'Numb_matchings':
                                Numb_card = eval(line.split("=")[1])
                            # highest_imp_player = best NE - utility alone
                            if 'alone' in line.split("=")[0]:
                                name_j = line.split("=")[0][6:-1]
                                province_scenarios[name_j][0] = eval(line.split("=")[1])
                            if 'low util' in line.split("=")[0]:
                                name_j = line.split("=")[0][9:]
                                province_scenarios[name_j][1] = eval(line.split("=")[1])
                            if 'high util' in line.split("=")[0]:
                                name_j = line.split("=")[0][10:]
                                province_scenarios[name_j][2] = eval(line.split("=")[1])
                            if line.split("=")[0]=='time_Uniform_Gen':
                                time_gen = eval(line.split("=")[1])
                                tl_gen = True
                            if line.split("=")[0]=='time for Verify all NE ':
                                time_NE = eval(line.split("=")[1])
                            if line.split("=")[0]=='low IA ':
                                run_all = True
                    if run_all:
                        ### can report statistics
                        highest_imp = {j:(province_scenarios[j][2]-province_scenarios[j][0]) for j in selected_names}
                        low_imp = {j:(province_scenarios[j][1]-province_scenarios[j][0]) for j in selected_names}
                        highest_imp_player = max(highest_imp.values())
                        name_highest = [short[j] for j in selected_names if highest_imp[j] == highest_imp_player]
                        name_highest = " ".join(name_highest)
                        lowest_imp_player = min(low_imp.values())
                        name_low = [short[j] for j in selected_names if low_imp[j] == lowest_imp_player]
                        name_low = " ".join(name_low)
                        if ins ==1:
                            f.write("%d & %s & %d & %d & %d & %.2f & %d & %s & %d & %s & %.2f & %.2f\\\ \n"%(Numb_V,ins,E,maxCard, Numb_card,per_NE, highest_imp_player,name_highest ,lowest_imp_player,name_low,time_gen,time_NE))
                        else: # do not repeat Numb_V
                            f.write(" & %s & %d & %d & %d & %.2f & %d & %s & %d & %s & %.2f & %.2f\\\ \n"%(ins,E,maxCard, Numb_card,per_NE, highest_imp_player,name_highest ,lowest_imp_player,name_low,time_gen,time_NE))
                    else: # did not finished
                        if tl_gen:
                            if ins ==1:
                                f.write("%d & %s & %d & %d & %d  &  &  & &  &  & %.2f & tl\\\ \n"%(Numb_V,ins,E,maxCard, Numb_card,time_gen))
                            else: # do not repeat Numb_V
                                f.write(" & %s & %d & %d & %d  &  &  & &  &  & %.2f & tl\\\ \n"%(ins,E,maxCard, Numb_card,time_gen))
                        else:
                            if ins ==1:
                                f.write("%d & %s & %d & %d &  &  &  & &  &  & tl & \\\ \n"%(Numb_V,ins,E,maxCard))
                            else: # do not repeat Numb_V
                                f.write(" & %s & %d & %d &   &  &  & &  &  & tl & \\\ \n"%(ins,E,maxCard))
    f.close()
    return None

if __name__ == "__main__":

    module = "from Run_Cardinality_test import *"
    mode = 'run_code' # or 'write' statistics
    if mode == 'write':
        Stats_Part(1000)
    if mode == 'run_code':
        #for Numb_V in [30,40,50]:
        for Numb_V in [30]:
            for high_sensitized in [2009]:
            #for high_sensitized in [2009,2013]:
                #for ins in range(21,31):
                for ins in [23]:
                # ins<11 all provinces
                # if 11<=ins<=20 then consider the 3 biggest provs
                # if 21<=ins<=30 then consider the biggest prov and the two smallest
                # if 31<=ins<40 then consider only small provs
                #for ins in range(11,12):
                    #name_ins = str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)
                    K = 1000
                    #K = 10
                    if os.name == 'nt':
                        G = Run_Cardinality_instance(Numb_V,K,high_sensitized,ins)
                    else:
                        test = "Run_Cardinality_instance(%d,%d,%d,%d)"%(Numb_V,K,high_sensitized,ins)
                        runTest = "python3 -c '%s; %s'"%(module, test)
                        runSub = " OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 12h %s"%(runTest) # Margarida
                        os.system(runSub)
                    if not os.path.isfile('Results/results_'+str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)+'.txt'):
                         shutil.copyfile('results.txt', 'Results/results_'+str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)+'.txt')
                #G = Run_Cardinality_instance(Numb_V,K,high_sensitized,ins)
