import os

if 'ildiko' in os.getcwd():
    venv_dir = '/Users/ildikop/Documents/projects/UiO-BigMed/bm_venv'
    activate_script = os.path.join(venv_dir, 'bin', 'activate_this.py')
    exec(compile(open(activate_script, 'rb').read(), activate_script, 'exec'), 
         dict(__file__=activate_script))

import spacy_udpipe
from to_linkage import Pedigree, Person

data_folder = '/Users/ildikop/Documents/projects/UiO-BigMed/NorSynthClinical/pal_annotate'

#ped = Pedigree('P1')
person = Person('kusin')
gender = person.get_gender()
person.add_condition('mutasjon')
person.add_condition('bla')
#print(person)

#print(ped)

nlp = spacy_udpipe.load('nb')
for rel_f in sorted(os.listdir(data_folder)):
    file_name, ext = tuple(rel_f.split('.'))  
    #if ext == ".uio":
    if rel_f == 'example1.uio': # dev version
        path_to_file = os.path.join(data_folder, rel_f)
        ped = Pedigree()
        ped.id = file_name 
        ped.populate(path_to_file, nlp)


