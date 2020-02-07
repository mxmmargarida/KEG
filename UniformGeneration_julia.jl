"""

License: MIT
Julia 1.02
Dynamic programming formulation to count number of matchings of maximum cardinality
"""

using Printf
# INPUT
# G - graph generated using Graph_generation
# Recursive_table - dictionary computed in CountingMatchings_rosso.jl with recursive approach
# maxCard - size of the maximum cardinality matching
using Distributions
function UniformMaxMatching_julia(G,E,Recursive_table,maxCard)
    set_V = sort(collect(keys(G)))
    s_aux = [1 for v in set_V]
    r = length(E)
    sol_M = [] # it will contain the edges in the generated matching
    for e in reverse(E)
        # e is in set_E with prob:
        aux = rand()
        if r-1== 0 # if r-1 = 0 then x_r must be added, otherwise sol_M alread had maxCard nodes and the algorithm had stopped
            prob_no_e = 0
        else
            # probability of x_e = 0
            prob_no_e = Recursive_table[r-1,maxCard,s_aux]/(Recursive_table[r,maxCard,s_aux])
        end
        if aux > prob_no_e
            # then x_e = 1
            append!(sol_M,[Set(e)])
            #s_aux = [1 if v not in e else 0 for v in set_V]
            s_aux = [if !(v in e) s_aux[j] else s_aux[j]-1 end for (j,v) in enumerate(set_V)]
            maxCard = maxCard - 1
        end
        r = r-1
        if maxCard == 0
            return sol_M
        end
    end
    return sol_M
end

# ask the number of matching to generate
function Uniform_Number(G,E,gen_num,info)
    # maximum cardinality
    maxCard = OptimalMatching(G,E)
    ## save maxCard
    if info==1
        maxCardinality = @sprintf "%d" maxCard
        fres = open("results.txt","a")
        write(fres,"maxCard= ",maxCardinality, " \n")
        close(fres)
    end
    ## end save
    r = length(E)
    s = Dict(v=>1 for v in keys(G))
    F_table,Numb_matchings= Count_Mat_Paper(G, maxCard,E,r,s,1)
    ## save number of maximum matchings
    Numb_OPT_matchings = @sprintf "%d" Numb_matchings
    if info==1
        fres = open("results.txt","a")
        write(fres,"Numb_matchings= ",Numb_OPT_matchings, " \n")
        close(fres)
    end
    ## end save
    fgen = open("tmp.txt","w")
    for _ in 1:gen_num
        gen_M =UniformMaxMatching_julia(G,E,F_table,maxCard)
        aux = 0
        for e in gen_M
            e = [v for v in e]
            if aux ==0
                write(fgen,"[{")
            else
                write(fgen,",{")
            end
            write(fgen,string(e[1])*","*string(e[2])*"}")
            aux = aux+1
        end
        if length(gen_M)==0
            write(fgen,"[{}]\n")
        else
            write(fgen,"] \n")
        end
    end
    close(fgen)
end
