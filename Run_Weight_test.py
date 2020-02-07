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

import random

import MaximumMatching_Kbest

# instances already created by Generate_instance_test on Run_Cardinality_test.py are added nodes
# optional: remove_prov: provinces not to be considered; to distinguish these instances ins must be >10
def Generate_weight_instance(Numb_V,high_sensitized=2009,ins=0,remove_prov=[]):
    # go to folder Instances and create a new file called Graph_30_1_2009_w
    name_ins = str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)
    name_ins_w = name_ins+'_w'
    f1 = open('Instances/Graph_'+name_ins_w,'w')
    f = open('Instances/Graph_'+name_ins,'r')
    # read numb. vertices, numb of arcs (i.e, 2 times the edges E)
    _, A = map(int,f.readline().split())
    f1.write(str(Numb_V)+"  "+str(A)+"\n")
    for _ in range(A):
        v1,v2,_ = map(int,f.readline().split())
        w = round(random.betavariate(2,2),2) #generate random weight with beta distribution
        f1.write(str(v1)+" "+str(v2)+" "+str(w)+"\n")
    f.close()
    f1.close()
    return None

def Read_weight_instance(Numb_V,high_sensitized=2009,ins=0):
    name_ins = str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)
    f = open('Instances/Graph_'+name_ins+"_players",'r')
    size_V = eval(f.readline())
    f.close()

    # read graph instance
    G = Graph({},None,len(size_V.keys()))
    f = open('Instances/Graph_'+name_ins+"_w",'r')
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
    checked_edges_w = {}
    for _ in range(add_E):
        v1, v2, w12 = map(float,f.readline().split())
        v1 = int(v1)
        v2 = int(v2)
        if {v1,v2} in checked_edges and v1!=v2:
            G.add_edge([v1,v2],[w12,checked_edges_w[(v2,v1)]])
        else:
            checked_edges.append({v1,v2})
            checked_edges_w[(v1,v2)]=w12
    f.close()
    return G, size_V


# input
# Numbe_v - total number of vertices
# name_ins - name of the instance
# K - number of K best weighted matchings to be generated
# OUTPUT
# save statistical results
def Run_Weight_instance(Numb_V,K,high_sensitized=2009,ins=0):
    name_ins = str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)+"_w"


    # STEP 1: read instance
    G, size_V = Read_weight_instance(Numb_V,high_sensitized,ins)

    # save vertices distribution
    # for exemple, in prob_dist British columbia and yukon are the first provinces
    # so they get vertices 1, 2, .., size_V['British Columbia & Yukon'] = G.V_player(1)
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

    # STEP 2: Generate the K best weighted matchings and verify if they are NE

    try:
        ti_time = time.time()
        SOL = MaximumMatching_Kbest.K_best(G, G.edges(), K)
        time_Kbest = time.time() - ti_time
        K = len(SOL)
        fres = open("results.txt","a")
        fres.write("maxWeight= %.2f \n"%(SOL[0][1]))
        fres.write("cardOfmaxWeight= %d \n"%(len(SOL[0][0])))
        fres.write("minWeight= %.2f \n"%(SOL[-1][1]))
        fres.write("cardOfminWeight= %.d \n"%(len(SOL[-1][0])))
        fres.write("Numb_matchings= %d\n"%(K))
        fres.write("time_K_Gen= %.2f \n"%(time_Kbest))
        fres.close()


        print("Matchings have been computed")

        #  STEP 3 : verify if a matching is a Nash equilibrium of the weighted game

        # count Nash equilibria
        count_NE = 0
        # lowest and highest number of international exchanges among computed NE
        low_International = SOL[0][1]+1
        high_International = 0
        # players payoff statistics
        low_players = {prov: SOL[0][1]+1 for prov in size_V.keys()}
        high_players = {prov: 0 for prov in size_V.keys()}
        t_ini = time.time()
        for j in range(K):
            gen_M = SOL[j][0]
            if VerifyNE.Verify_NE(gen_M,G):
                if count_NE==0:
                    epsilon_of_SWE = SOL[0][1]-SOL[j][1]
                    epsilon_iteration = j
                count_NE = count_NE + 1
                # save players utilities and M
                # save worst and best M for each player
                for i,prov in enumerate(size_V.keys()):
                    if G.MatchingValue(i+1,gen_M)>high_players[prov]:
                        high_players[prov] = G.MatchingValue(i+1,gen_M)
                    if G.MatchingValue(i+1,gen_M)<low_players[prov]:
                        low_players[prov] = G.MatchingValue(i+1,gen_M)
                # save international RESULTS
                IA_match = sum([G.weight([e[0],e[1]])+G.weight([e[1],e[0]]) for e in G.EdgesExt() if set(e) in gen_M])
                if IA_match> high_International:
                    high_International = IA_match
                if IA_match< low_International:
                    low_International = IA_match
                # end saving results
        t_final = (time.time()-t_ini)/K

        # save NE results
        fres = open("results.txt","a")
        fres.write("time for Verify all NE = %.2f \n"%(t_final))
        fres.write("Numb_NE = "+ str(count_NE)+"\n")
        fres.write("K = "+ str(K)+"\n")
        if count_NE>=1:
            fres.write("epsilon_of_SWE = %.2f\n"%(epsilon_of_SWE))
            fres.write("epsilon_iteration = %d\n"%(epsilon_iteration))
        for prov in size_V.keys():
            fres.write("high util %s= %.2f\n"%(prov,high_players[prov]))
            fres.write("low util %s= %.2f\n"%(prov,low_players[prov]))
        fres.write("high IA = %.2f\n"%(high_International))
        fres.write("low IA = %.2f\n"%(low_International))
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
    f = open("Results/table_weight.txt",'w')
    for Numb_V in [30,40,50]:
        for high_sensitized in [2009,2013]:
            for ins in range(21,31):
                # [alone, low, high]
                province_scenarios = {j:[1,1,1] for j in prov_names}
                if os.path.isfile('Results/results_'+str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)+'_w.txt'):
                    run_all = False # did not terminated all computations
                    tl_gen = False # not enough time to generate
                    with open('Results/results_'+str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)+'_w.txt', 'r') as fresults:
                        for line in fresults:
                            if line.split("=")[0] == 'E ':
                                E = eval(line.split("=")[1])
                            if line.split("=")[0] == 'maxWeight':
                                maxWeight = eval(line.split("=")[1])
                            if line.split("=")[0] == 'cardOfmaxWeight':
                                cardOfmaxWeight = eval(line.split("=")[1])
                            if line.split("=")[0] == 'minWeight':
                                minWeight = eval(line.split("=")[1])
                            if line.split("=")[0] == 'cardOfminWeight':
                                cardOfminWeight = eval(line.split("=")[1])
                            if line.split("=")[0] == 'Numb_NE ':
                                Numb_NE = eval(line.split("=")[1])
                            if line.split("=")[0] == 'K ':
                                K = eval(line.split("=")[1])
                                per_NE = 100*((Numb_NE*1.)/K)
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
                            if line.split("=")[0]=='time_K_Gen':
                                time_gen = eval(line.split("=")[1])
                                tl_gen = True
                            if line.split("=")[0]=='time for Verify all NE ':
                                time_NE = eval(line.split("=")[1])
                            if line.split("=")[0]=='low IA ':
                                lowIA = eval(line.split("=")[1])
                                run_all = True
                            if line.split("=")[0]=='high IA ':
                                highIA = eval(line.split("=")[1])
                            if line.split("=")[0]=='epsilon_of_SWE ':
                                epsilon_of_SWE = eval(line.split("=")[1])
                            if line.split("=")[0]=='epsilon_iteration ':
                                epsilon_iteration = eval(line.split("=")[1])
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
                        if ins in [1,11,21]:
                            if Numb_NE>0:
                                f.write("%d & %s & %d & %.2f & %d & %.2f & %.2f & %d & %.2f & %s & %.2f & %s & %.2f & %.2f & %.2f & %.2f\\\ \n"%(Numb_V,ins,E,maxWeight, K,per_NE, epsilon_of_SWE,epsilon_iteration, highest_imp_player,name_highest ,lowest_imp_player,name_low,highIA,lowIA,time_gen,time_NE))
                            else:
                                f.write("%d & %s & %d & %.2f & %d & %.2f & %s & & & &  & &   &   & %.2f & %.2f\\\ \n"%(Numb_V,ins,E,maxWeight, K,0, '>'+str(round(maxWeight-minWeight,2)),time_gen,time_NE))
                        else: # do not repeat Numb_V
                            if Numb_NE>0:
                                f.write(" & %s & %d & %.2f & %d & %.2f & %.2f & %d & %.2f & %s & %.2f & %s & %.2f & %.2f & %.2f & %.2f\\\ \n"%(ins,E,maxWeight, K,per_NE, epsilon_of_SWE,epsilon_iteration, highest_imp_player,name_highest ,lowest_imp_player,name_low,highIA,lowIA,time_gen,time_NE))
                            else:
                                f.write(" & %s & %d & %.2f & %d & %.2f & %s & & & &  & &   &   & %.2f & %.2f\\\ \n"%(ins,E,maxWeight, K,0, '>'+str(round(maxWeight-minWeight,2)),time_gen,time_NE))
                    else: # did not finished
                        if tl_gen:
                            if ins in [1,11,21]:
                                f.write(" %d & %s & %d & %.2f & %d & & & &  & & & &  & & %.2f & tl\\\ \n"%(Numb_V,ins,E,maxWeight, K,time_gen))
                            else:
                                f.write(" & %s & %d & %.2f & %d & &  & & & & & &  & & %.2f & tl\\\ \n"%(ins,E,maxWeight, K,time_gen))
                        #VOU AQUI
                        else:
                            if ins in [1,11,21]:
                                f.write(" %d & %s & %d & %.2f & %d & &  & & & & & &  & & tl & tl\\\ \n"%(Numb_V,ins,E,maxWeight, K))
                            else:
                                f.write(" & %s & %d & %.2f & %d & &  & & & & & &  & & tl & tl\\\ \n"%(ins,E,maxWeight, K))
    f.close()
    return None

if __name__ == "__main__":

    module = "from Run_Weight_test import *"
    #mode = 'run_code' # or 'write' statistics
    mode = 'run_code'
    if mode == 'write':
        remove_prov = ['British Columbia & Yukon', 'Alberta', 'Saskatchewan', 'Manitoba',  'Nova Scotia', 'New Brunswick', 'Newfoundland and Labrador']
        #remove_prov = []
        #remove_prov =  ['Saskatchewan', 'Manitoba','Quebec', 'Nova Scotia', 'New Brunswick', 'Prince Edward Island', 'Newfoundland and Labrador']
        Stats_Part(1000,remove_prov)
    if mode == 'run_code':
        #for Numb_V in [30,40,50]:
        for Numb_V in [30]:
            for high_sensitized in [2009]:
            #for high_sensitized in [2009,2013]:
                #for ins in range(21,31):
                for ins in [22]:
                # ins<11 all provinceszs
                # if 11<=ins<=20 then consider the 3 biggest provs
                # if 21<=ins<=30 then consider the biggest prov and the two smallest
                # if 31<=ins<40 then consider only small provs
                #for ins in range(1,2):
                    #name_ins = str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)
                    K = 1000
                    #K = 10
                    if os.name == 'nt':
                        G = Run_Weight_instance(Numb_V,K,high_sensitized,ins)
                    else:
                        test = "Run_Weight_instance(%d,%d,%d,%d)"%(Numb_V,K,high_sensitized,ins)
                        runTest = "python3 -c '%s; %s'"%(module, test)
                        runSub = " OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 timeout 2h %s"%(runTest) # Margarida
                        os.system(runSub)
                    if not os.path.isfile('Results/results_'+str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)+'_w.txt'):
                         shutil.copyfile('results.txt', 'Results/results_'+str(Numb_V)+"_"+str(ins)+"_"+str(high_sensitized)+'_w'+'.txt')
                #G = Run_Cardinality_instance(Numb_V,K,high_sensitized,ins)
