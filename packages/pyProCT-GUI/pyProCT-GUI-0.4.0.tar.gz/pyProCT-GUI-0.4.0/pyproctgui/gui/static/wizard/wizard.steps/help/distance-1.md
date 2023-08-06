## Generating an euclidean distance matrix
In this step you will be able to define how an euclidean distance matrix will be calculated. In brief, this matrix will hold the pairwise distances
of the geometrical centers of one part of the loaded structure (defined through a selection string). This kind of matrices are
specially useful to cluster ligands in ligand-protein explorations for instance.

In order to calculate this kind of matrix, the first thing pyProCT needs is to superpose all the frames of your trajectory. Instead of using
a reference frame, it tries to minimize the RMSD o all frames by using an iterative superposition scheme. As user you will be responsible
of deciding what to superpose. For instance, if you want to superpose Alpha Carbons you will have to write a with a ProDy
compatible selection string (see <a href="http://www.csb.pitt.edu/prody/reference/atomic/select.html" target="_blank">this</a>) as "*name CA*" inside the
"*Superposition selection*" field.
The next step will be to define the atoms you will use to in the distance calculation by writing another selection string in the
"*Calculation selection*" field (i.e. "*chain B*" if your ligand is tagged as chain B in the PDB file).
Push the enter key after writing your selection to make the little previewer on your right show the outcome of your selection.