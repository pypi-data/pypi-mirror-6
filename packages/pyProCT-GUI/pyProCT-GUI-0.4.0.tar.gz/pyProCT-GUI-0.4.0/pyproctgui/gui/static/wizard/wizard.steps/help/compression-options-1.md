## Compression options
Set here the options you want to use for the compression protocol.  

- Maximum number of frames:  is the number of frames we want to have in the output trajectory. The final trajectory can have less 
frames if needed.  

- Compression type: defines the algorithm used for the compression step. If "*RANDOM*" is chosen, a random sample
of each cluster will be used to form the output trajectory. If "*KMEDOIDS*" is used instead, it will use K-Medoids, so 
the final distances of the output trajectory will be distributed more evenly.
