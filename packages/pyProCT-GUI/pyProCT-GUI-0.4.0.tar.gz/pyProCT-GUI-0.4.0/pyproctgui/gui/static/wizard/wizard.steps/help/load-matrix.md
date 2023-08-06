## Using a predefined matrix
If you want to use a distance funtion different of the ones provided (euclidean distance and RMSD) you can generate your matrix
using a separate program. pyProCT uses [pyRMSD](https://github.com/victor-gil-sepulveda/pyRMSD.git)'s condensed matrices. Take a look to its documentation to discover how to handle and
save them (the MatrixHandler class in pyproct.driver.handler.matrix.matrixHandler can also give you some hints about its use).  

The only way to choose the matrix file is by using the browse button and selecting one from your filesystem. 
