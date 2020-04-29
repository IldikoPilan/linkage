
import os
import sys
import subprocess
import spacy_udpipe
from Pedigree import Pedigree

def rel_to_linkage(path_to_file, nlp, out_dir): 
    """ Transform entity and relation annotation tags into LINKAGE format
    and save it to a .ped file .
    """
    ped = Pedigree()
    path, file_name = os.path.split(path_to_file)
    ped.id = file_name 
    ped.populate(path_to_file, nlp, out_dir)
    return ped

def linkage_to_plot(linkage_f, out_f='', names=[]):
    """ Run R script to plot from LINKAGE format (with the kinship2 R package).
    """
    if not out_f:
        out_f = os.path.splitext(os.path.split(linkage_f)[1])[0] + ".png"
    if names:
        command = "Rscript plot_pedigree.r {} {} {}".format(linkage_f, out_f, names)
    else:
        command = "Rscript plot_pedigree.r {} {}".format(linkage_f, out_f)
    subprocess.call(command.split())

def main(path_to_input, out_dir=''):   
    """ Generate plot for an input file or multiple files in a folder.
    """
    nlp = spacy_udpipe.load('nb')
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    if os.path.isdir(path_to_input):   # folder as input
        for rel_f in sorted(os.listdir(path_to_input)):
            file_name, ext = os.path.splitext(rel_f)
            out_f = os.path.join(out_dir, file_name+".png")
            if ext == ".uio":
                path_to_file = os.path.join(path_to_input, rel_f)
                pedigree = rel_to_linkage(path_to_file, nlp, out_dir)
                linkage_f = os.path.join(out_dir, file_name+'.ped') 
                names = ",".join(list(pedigree.id_mapping.keys()))
                #linkage_to_plot(linkage_f, out_f, names) # TO DO: finish
    else:                              # file as input
        path, file_name = os.path.split(path_to_input)
        file_name, ext = os.path.splitext(file_name)
        linkage_f = os.path.join(out_dir, file_name+'.ped') 
        out_f = os.path.join(out_dir, file_name+".png")
        if path_to_input.endswith('.uio'): # TO DO: load pedigree obj from .pkl
            pedigree = rel_to_linkage(path_to_input, nlp, out_dir)
            names = ",".join(list(pedigree.id_mapping.keys()))
            linkage_to_plot(linkage_f, out_f, names)
        elif file_name == 'example1_gold': # get a gold standard plot
            id_mapping = {'pasient': 1, 'mor': 2, 'far': 5, 'farmor': 6, 
                          'farfar': 7, 'farbror': 8, 'søster': 9, 'fetter': 10, 'fetter2': 11, 
                          'tante': 12, 'bror': 13, 'barn': 14, 'partner': 15, 'barn2': 16}
            names = ",".join(list(id_mapping.keys()))
            linkage_to_plot(linkage_f, out_f, names)
        elif path_to_input.endswith('.ped'):
            print('in gen')
            linkage_to_plot(linkage_f, out_f)
            # TO DO: parse additional arg with names?
        else:
            raise ValueError('Input file(s) must have the extension .ped or .uio')

if __name__ == "__main__":
    data_folder = sys.argv[1] 
    out_dir = sys.argv[2]  # optional
    main(data_folder, out_dir)

"""
Do next:
- aff: 0=unaffected, 1=aff NA = unknown
- INDEX -> aff=1
- anything unknown > NA
- status param -> 1=dead 0=censored (p 18)
- check plot error with gender: if manually edited, same format works -> spacing issue? integer conv issue? (tab same issue)  
- implement LINKAGE format save (switch to int IDs)
- creating name-intID mapping attrib for Pedigree
- handle other terms (ambiguous and non 'farfar hadde 2 brødre') etc to related to 
- add information to multiple members of same type appearing *after* AMOUNT 
- Modifier with NEG: use to add/modify info in Person.conditions  -> uncertainty AND negation!


Other to dos:
- Handle Modifier AMOUNT - COND / EVENT
- Handle Subset -> COND when updating mmember info added with AMOUNT
- FAMILY:   
    mor/far for halvbror
    sibling addition handled for: patient and mor/far (not others)
    family terms not always relative to SELF (pasient) e.g. text2 'Farfar hadde to brødre' 'farens bror'
- pronouns
    use for updating info on last mentioned Person.id
    use for disambiguating gender for genderless FAMILY (e.g. barn)
- add missing family terms: søskenbarn, sønnesønn, oldemor, oldefar, forelder
- move global vars not used in Person to Pedigree attribs?
- process relations in a certain order?
- check if 'farens bror' annotated as Related_to
- add pedigree ID in final LINKAGE format
P - switch defaults to unknown
- check how to solve aff unknown (0 not valid value)
(- marker_genotypes after phenotype column)
(- AGE)
- remove superflous: parents added even if not appearing in text -> remove subsequently when not used
(- tvilling -> can be added in kinship2) 

Done

- move update_side to Pedigree
- duplicate entries
- move relation to separate function
- remove pasient from conditions
- infer patient gender
- write an R script with code to generate plot
- write a bash script that execute first the Python and then the R script (or write a Python binding to R?)
- gender -> 3=unknown


"""


