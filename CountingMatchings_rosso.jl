"""
License: MIT
Julia 1.02
Dynamic programming formulation to count number of matchings of maximum cardinality
"""

# function from the paper
# INPUT:
# G and E - can be provided by read_Graph(filename)
# maxCard - can be prodived by OptimalMatching(G,E)
function Count_Mat_Paper(G, maxCard,E,r,s,aux)
    # reset table of results
    if aux == 1
        global F_table = Dict()
    end
    # do not repeat computations:
    try
        # if aux == 1 then that entry wont exist
        return F_table[r,maxCard,[if s[v]>0 1 else 0 end for v in sort(collect(keys(G)))]]
    catch
        # if any of the entries maxCard, r or s is negative return 0
        if maxCard<0 || r<0 || minimum(values(s))<0
            F_table[r,maxCard,[if s[v]>0 1 else 0 end for v in sort(collect(keys(G)))]]=0
            # aux =1 means we are in the end of the recurssion so return table
            if aux ==1
                return F_table, 0
            end
            # if not in end of the recurssion return 0 (no need to return table since it is a global variable)
            return 0
        end
        # matchings containing more edges than the ones available
        if maxCard>r
            F_table[r,maxCard,[if s[v]>0 1 else 0 end for v in sort(collect(keys(G)))]]=0
            # aux =1 means we are in the end of the recurssion so return table
            if aux ==1
                return F_table, 0
            end
            # if not in end of the recurssion return 0 (no need to return table since it is global variable)
            return 0
        end
        # if we want a matching of cardinality 0, the only choice is M= empty set, i.e., there only one solution
        if maxCard ==0 && r >=0 && minimum(values(s))>=0
            F_table[r,maxCard,[if s[v]>0 1 else 0 end for v in sort(collect(keys(G)))]]=1
            # aux =1 means we are in the end of the recurssion so return table
            if aux ==1
                return F_table, 1
            end
            # if not in end of the recurssion return 0 (no need to return table since it is global variable)
            return 1
        # if there are no edges available, i.e., r=0, and maxCard>0 then there is no matching under these condition
        elseif maxCard >0 && r ==0 && minimum(values(s))>=0
            F_table[r,maxCard,[if s[v]>0 1 else 0 end for v in sort(collect(keys(G)))]]=0
            # aux =1 means we are in the end of the recurssion so return table
            if aux ==1
                return F_table, 0
            end
            # if not in end of the recurssion return 0 (no need to return table since it is global variable)
            return 0
        # OPT >0 and r>0 and min(s)>=0
        else
            No_r = Count_Mat_Paper(G,maxCard,E,r-1,s,0)
            Yes_r = Count_Mat_Paper(G,maxCard-1,E,r-1,Dict(if v in E[r] v=>s[v]-1 else v=>s[v] end for v in sort(collect(keys(G)))),0)
            F_table[r,maxCard,[if s[v]>0 1 else 0 end for v in sort(collect(keys(G)))]] = No_r+Yes_r
            if aux ==1
                return F_table,No_r+Yes_r
            end
            return No_r+Yes_r
        end
    end
end

# read graphs

function Read_Graph(filename)
    G_tpm = Dict()
    f = open(filename)
    lines =  readlines(f)
    close(f)
    num_V, num_E = split(lines[1])
    num_V = parse(Int,num_V)
    num_E = parse(Int,num_E)
    for i=1:num_E
        v1,v2,w = split(lines[1+i])
        v1 = parse(Int,v1)
        v2 = parse(Int,v2)
        if !(v2 in keys(G_tpm))
            G_tpm[v2] = []
        end
        if !(v1 in keys(G_tpm))
            G_tpm[v1] = [v2]
        else
            append!(G_tpm[v1],v2)
        end
    end
    G = Dict(v=>[] for v in keys(G_tpm))
    E = []
    for v1 in keys(G_tpm)
        for v2 in G_tpm[v1]
            if v1 in G_tpm[v2] && !(v1 in G[v2]) && !(v2 in G[v1])
                append!(G[v1],v2)
                append!(G[v2],v1)
                append!(E,[Set([v1,v2])])
            end
        end
    end
    if length(keys(G))==0
        G = Dict(v=>[] for v in 1:num_V)
    end
    return G,E
end



using CPLEX, JuMP
function OptimalMatching(G,E)
    #m = Model(solver=CplexSolver())
    m = Model(with_optimizer(CPLEX.Optimizer))
    # only one core:
    CPX_PARAM_THREADS = 1
    CPX_PARAM_MIPDISPLAY =0
    CPX_PARAM_TILIM = 3600
    num_E = length(E)
    if num_E==0
        return 0
    end
    @variable(m, x[1:num_E], Bin)
    for v in keys(G)
        @constraint(m,sum(x[j[1]] for j in enumerate(E) if v in j[2])<=1)
    end
    @objective(m, Max, sum(x[j[1]] for j in enumerate(E)))
    optimize!(m)
    println("Objective value: ", objective_value(m))
    #println("Objective value: ", getobjectivevalue(m))
    return objective_value(m)
end
