# to be used by Run_UniformGeneration.py

using Pkg
Pkg.activate(".")
# you can comment the command below after running this script for the first time
Pkg.instantiate()

include("CountingMatchings_rosso.jl")
include("UniformGeneration_julia.jl")

# pre compilation with easy example
G,E = Read_Graph("auxiliar_instance")
time_cpu = @elapsed Uniform_Number(G,E,2,0)

# filename given by python
G,E = Read_Graph("Graph_file")
f = open("size")
lines =  readlines(f)
close(f)
lines=split(lines[1])
# gen_NUM is the K, i.e, the number of optimal matchings to be generated
gen_NUM =parse(Int,lines[1])
# gen_NUM given by python
time_cpu = @elapsed Uniform_Number(G,E,gen_NUM,1)
time_cpu = @sprintf "%.2f" time_cpu

# save computational results
fres = open("results.txt","a")
write(fres,"time_Uniform_Gen= ",time_cpu, " \n")
close(fres)
