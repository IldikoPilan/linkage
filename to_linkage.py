
import os
import sys
import subprocess
import spacy_udpipe
from Pedigree import Pedigree

def rel_to_linkage(path_to_file, nlp): 
    """ Transform entity and relation annotation tags into LINKAGE format.
    """
    print(path_to_file)
    ped = Pedigree()
    path, file_name = os.path.split(path_to_file)
    print(file_name)
    ped.id = file_name 
    ped.populate(path_to_file, nlp)
    return ped

def linkage_to_plot(pedigree, linkage_f, out_f=''):
    """ Run R script to plot from LINKAGE format (with the kinship2 R package).
    # TO DO: get saved file from rel_to_linkage 
    # TO DO: get family names from a pedigree attribute with ID mappings
    """
    if not out_f:
        out_f = os.path.split(linkage_f)[1].split('.')[0] + ".png"
    names = "pasient,mor,far" 
    command = "Rscript plot_pedigree.r {} {} {}".format(linkage_f, out_f, names)
    subprocess.call(command.split())

def main(path_to_input):   
    """ Generate plot for an input file or multiple files in a folder.
    """
    nlp = spacy_udpipe.load('nb')
    if os.path.isdir(path_to_input):   # folder as input
        for rel_f in sorted(os.listdir(path_to_input)):
            file_name, ext = tuple(rel_f.split('.'))  
            if ext == ".uio":
                path_to_file = os.path.join(path_to_input, rel_f)
                pedigree = rel_to_linkage(path_to_file, nlp)
                #linkage_to_plot(pedigree, linkage_f) # TO DO: finish
    else:                              # file as input
        pedigree = rel_to_linkage(path_to_input, nlp)
        # dev version files
        linkage_f = "/Users/ildikop/Documents/projects/UiO-BigMed/NorSynthClinical/to_linkage/examples/test.ped"
        out_f = "examples/test.png"
        linkage_to_plot(pedigree, linkage_f, out_f)

if __name__ == "__main__":
    data_folder = sys.argv[1] 
    main(data_folder)

"""
Do next:
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
(- marker_genotypes after phenotype column)
(- AGE)
- remove superflous: parents added even if not appearing in text -> remove subsequently when not used

Done

- move update_side to Pedigree
- duplicate entries
- move relation to separate function
- remove pasient from conditions
- infer patient gender
- write an R script with code to generate plot
- write a bash script that execute first the Python and then the R script (or write a Python binding to R?)
"""


