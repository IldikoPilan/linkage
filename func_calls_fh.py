import os
import subprocess

if 'ildiko' in os.getcwd():
    venv_dir = '/Users/ildikop/Documents/projects/UiO-BigMed/bm_venv'
    activate_script = os.path.join(venv_dir, 'bin', 'activate_this.py')
    exec(compile(open(activate_script, 'rb').read(), activate_script, 'exec'), 
         dict(__file__=activate_script))

import spacy_udpipe
from Person import Person
from Pedigree import Pedigree

data_folder = '/Users/ildikop/Documents/projects/UiO-BigMed/NorSynthClinical/pal_annotate'

#ped = Pedigree('P1')
person = Person('kusin')
gender = person.get_gender()
person.add_condition('mutasjon')
person.add_condition('bla')
#print(person)
#print(ped)

# Run R script to plot from LINKAGE format (with the kinship2 R package)
# From Sublime
#subprocess.call("/Users/ildikop/Documents/projects/UiO-BigMed/NorSynthClinical/to_linkage/test1.r") 

