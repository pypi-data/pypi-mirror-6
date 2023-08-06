## K-Medoids Algorithm
Uncheck the checkbox in case you prefer to define your own parameters for this algorithm.
In that case you will be able to define how the seeding step of the algorithm will be preformed. If 'RANDOM' is selected, the first k medoids
will be randomly chosen. If 'EQUIDISTANT' is selected, pyProCT will select equiseparated elements (in terms of their position into the trajectory) as medoids. Finally,
if 'GROMOS' is used, pyProCT will try different cutoff values for the GROMOS algorithm and it will use the cluster representatives of the first k sized clustering
obtained.

'number of clusters' is a list of integers. In this cases users can explicitly write a comma separated list of integers, or use this a contracted list definition.
Conntracted lists are a list of 3 integer numbers with this layout:
    a,b:c

Meaning that the defined list goes from 'a' to 'b' (included), and each element is defined after 'c' steps e.g.:
    1,10:2 = [1,3,5,7,9] ,
    2,6:1 = [1,2,3,4,5,6]
