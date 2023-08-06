## Spectral Algorithm
Uncheck the checkbox in case you prefer to define your own parameters for this algorithm.
In that case you will be able to define a list of sigma values (to calculate the adjacency matrix) and the number of clusters the algorithm
has to produce. Sigma and number of clusters are combined to get the parameters e.g:

If:
	'sigma' = 1, 1.5
and:
	'number of clusters' = 3,8

Then spectral clustering will be run with parameters (1,3) , (1,8) , (1.5,3) and (1.5,8).

'number of clusters' is a list of integers. In this cases users can explicitly write a comma separated list of integers, or use this a contracted list definition.
Conntracted lists are a list of 3 integer numbers with this layout:
    a,b:c

Meaning that the defined list goes from 'a' to 'b' (included), and each element is defined after 'c' steps e.g.:
    1,10:2 = [1,3,5,7,9] ,
    2,6:1 = [1,2,3,4,5,6]
