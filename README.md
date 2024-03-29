# Kidney Exchange Game

This is the code necessary for the experiments presented in

[*M. Carvalho, A. Lodi, "A theoretical and computational equilibria analysis of a multi-player kidney exchange program", 2022.European Journal of Operational Research*](https://www.sciencedirect.com/science/article/pii/S0377221722004039#sec0012)

[*M. Carvalho, A. Lodi, "Game theoretical analysis of Kidney Exchange Programs", 2020.*](https://arxiv.org/abs/1911.09207)

<sup> Remark: The random instances generator is available under request. Requests must provide names and affiliations of the researchers involved in the project using the generator, as well as the project title. This information will be forward to the Canadian Blood Services. <sup>

These implementations used Python 3, Julia 1.02 and CPLEX 12.9.0.

## Instances and Results

In the folder CanadianInstances/, all instances used in the paper are available; they were generated by our simulator that uses data from the Canadian Kidney Paired Donation Program. Their name is accordingly with Section 4.1.1 of the arxiv paper. Instances ending in 'w' are exactly the same as the ones without 'w' with the exception that weights on graphs are not necessarily unitary. Instances ending in 'players' reflect the vertices that belong to each player in the graph described by the file without 'players'. Note that graph vertices have labels starting in one, thus if e.g. we have 'British Columbia & Yukon': 10 and 'Alberta': 4, it means that the vertices from 1 to 10 belong to British Colombia & Yukon, and the vertices from 11 to 14 belong to Alberta.

For each file in CanadianInstances/, the first line indicates the number of vertices and arcs. The remaining lines, have the format
```js
v1 v2 w
```
i.e., there is an arc from vertice v1 to vertice v2 with weight w.

In the folder Results/, all the results from the paper are available.

## Python Code


The code ``` Graph_Generation.py``` implements the python class for the compatability graphs. Note: pydot is used to draw graphs; if you do not have, just comment the function of the graph class ``` print_game ```.

The code ```MaximumMatching_Kbest.py``` allows to determine the K best maximum weighted matchings (see paper for a reference). It uses the function ```K_best(G, set_E, K)``` to build all subproblems for which a maximum matching is determined through ``` OptimalMatching(G, set_E, x_fix_0, x_fix_1)```.

The code ```Run_Cardinality_test.py``` has all necessary algorithms to uniformly generate matchings of maximum cardinality (``` UniformGen_Python_to_Julia.jl``` ), verify if they are Nash equilibria (``` VerifyNE.py``` ), and to compute all statistics for the tables in the paper.

The code ```Run_Weight_test.py``` has all necessary algorithms to uniformly generate the K matchings of maximum weight (```MaximumMatching_Kbest.py```) and verify if they are Nash equilibria (```VerifyNE.py```).

The code ```VerifyNE.py``` makes the verification of NE for W-KEG (note that #-KEG can be determined by making weights equal to 1).
