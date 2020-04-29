
import os
import sys
import subprocess
import spacy_udpipe
from Pedigree import Pedigree

def rel_to_linkage(path_to_file, nlp, out_dir): 
    """ Transforms entity and relation annotation tags into LINKAGE format
    and save it to a .ped file .
    """
    ped = Pedigree()
    path, file_name = os.path.split(path_to_file)
    ped.id = file_name 
    ped.populate(path_to_file, nlp, out_dir)
    return ped

def linkage_to_plot(linkage_f, out_f='', names=[]):
    """ Runs R script to plot from LINKAGE format (with the kinship2 R package).
    """
    if not out_f:
        out_f = os.path.splitext(os.path.split(linkage_f)[1])[0] + ".png"
    if names:
        command = "Rscript to_linkage/plot_pedigree.r {} {} {}".format(linkage_f, out_f, names)
    else:
        command = "Rscript to_linkage/plot_pedigree.r {} {}".format(linkage_f, out_f)
    subprocess.call(command.split())

def main(path_to_input, out_dir=''):   
    """ Generates plot for an input file or multiple files in a folder.
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

data_folder = sys.argv[1] 
out_dir = sys.argv[2]  
main(data_folder, out_dir)




