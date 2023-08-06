'''
Created on 08/05/2013

@author: victor
'''
import os
import prody
import urllib2


def get_elements (pdb):
    pdb_elements = pdb.getElements()
    names = pdb.getNames()
    elements = []
    for i, element in  enumerate(pdb_elements):
        if len(element) == 0:
            elements.append(names[i][0])
        else:
            elements.append(element)
    return elements        
    
def get_pdb_selection(data):
    pdb_file = data['pdb']
    selection_string = data['selection']
    base_workspace = data['base']
    
    if selection_string == "":
        return "EMPTY"
    
    # First extract the first frame
    pdb_file_handler = open(pdb_file,"r")
    
    for line in pdb_file_handler:
        if line[0:5] == "MODEL":
            break
        
    first_frame_lines = line
    for line in pdb_file_handler:
        if line[0:5] == "MODEL" or line[0:6] == "ENDMDL":
            break
        else:
            first_frame_lines += line
    
    first_frame_lines += "ENDMDL\n"
    pdb_file_handler.close()
    open(os.path.join(base_workspace,"tmp_pdb_first_frame"),"w").write(first_frame_lines)
    
    selection = None
    try:
        selection = prody.parsePDB(os.path.join(base_workspace,"tmp_pdb_first_frame")).select(selection_string)
    except prody.SelectionError:
        return "ERROR:MalformedSelection"
    except AttributeError:
        return "ERROR:MalformedSelection"
    
    if selection == None or len(selection.getCoordsets()) == 0:
        return "ERROR:ImproductiveSelection"
    
    selection_coordsets = selection.getCoordsets()[0]
    number_of_atoms = selection_coordsets.shape[0]
    atom_elements = get_elements (selection)

    lines = ["%d\n"%(number_of_atoms),"%s first frame\n"%(pdb_file)]
    for i in range(number_of_atoms):
        initial_string = "  %s"%atom_elements[i]
        coord_triplet = selection_coordsets[i]
        for coord in coord_triplet:
            initial_string+=("%10.5f"%coord).rjust(15)
        lines.append(initial_string+"\n")
        
    #open(os.path.join(base_workspace,"selection_output"),"w").write("".join(lines))  
    return urllib2.quote("".join(lines))