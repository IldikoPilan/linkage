
import os

global variants
global family_relations
global ambiguous_side
global ambiguous_gender

variants = {'broder': 'bror', 
            'fader':'far',
            'mor' : 'moder', 
            'fett':'fetter'     # UDPipe tokenization issue
            }

family_relations = {
    ('partner', 'pasient') : ['datter', 'sønn', 'barn'],
    ('mor', 'far') : ['pasient', 'søster', 'halvsøster', 'bror', 'halvbror'],
    #('bestemor', 'bestefar'): ['mor', 'far', 'tante', 'onkel'],
    ('mormor', 'morfar') : ['mor', 'tante', 'onkel', 'moster', 'morbror'],
    ('farmor', 'farfar') : ['far', 'tante', 'onkel', 'faster', 'farbror'],
    #('tante', 'onkel'): ['kusine', 'fetter'],
    ('faster', 'onkel') : ['kusine', 'fetter'],
    ('moster', 'onkel') : ['kusine', 'fetter'],
    ('tante', 'farbror') : ['kusine', 'fetter'],
    ('tante', 'morbror') : ['kusine', 'fetter'],
    #('søsken', 'svigersøsken'): ['niese', 'nevø'],
    ('søster', 'svigerbror') : ['niese', 'nevø'],
    ('svigersøster', 'bror') : ['niese', 'nevø']
    }

ambiguous_side = ['bestemor', 'bestefar','tante', 'onkel', 'kusine', 'fetter', 'niese', 'nevø']
ambiguous_gender = ['barn', 'søsken', 'forelder'] 
amounts = {'en':1, 'to':2, 'tre':3, 'fire':4, 'fem':5}


def read_relations(path_to_file):
    """ Reads information from .uio file format with
    relations. Returns a nested list where sub-lists
    contain the follwing token-level information.
    """
    relation_info = []
    with open(path_to_file) as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("# sent_id =  "):
                #sent_id += 1
                continue
            elif line == "\n":
                continue
            elif line.startswith("# text =  "):
                sent = line[10:-1]
                #sentences[sent_id] = sent
            else:
                line_elem = line.strip().split("\t")
                relation = line_elem[1]
                entity_tag_orig, l_ix_orig, r_ix_orig = line_elem[2].split(",")
                entity_tok_orig = sent[int(l_ix_orig):int(r_ix_orig)]
                entity_tag_target, l_ix_target, r_ix_target = line_elem[3].split(",")
                entity_tok_target = sent[int(l_ix_target):int(r_ix_target)]
                relation_info.append([relation, entity_tag_orig, entity_tok_orig, 
                                      entity_tag_target, entity_tok_target])
    return relation_info

class Person:
    def __init__(self, person_id):
        self.id = person_id
        self.father = 0
        self.mother = 0
        self.siblings = []
        self.gender = None
        self.index_cond_val = 0
        self.other_conditions = {} # {cond_name: 0 / 1 / 2}
    
    def __str__(self):
        if self.father:
            father = self.father.id
        else:
            father = self.father
        if self.mother:
            mother = self.mother.id
        else:
            mother = self.mother
        out = '{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}'.format(self.id, father, mother, self.gender, self.index_cond_val, '\t'.join(['{}'.format(cond) 
                                            for (cond, val) in self.other_conditions.items()]))
        return out

    def get_gender(self):
        """ Returns numeric value corresponding to gender 
        (0 = unknown, 1 = male, 2 = female).
        E.g. 0: forelder, sysken, tvilling, barn, kusin
        """
        gender = 0
        gender_info = {'2' : ['mor', 'søster', 'datter', 'tante', 'faster', 'moster',
                              'niese', 'kone', 'hustru', 'kusine'],
                       '1' : ['far', 'bror', 'sønn', 'onkel', 'farbror', 'morbror', 
                              'nevø', 'man', 'husbond', 'fetter'],
                       '0' : ambiguous_gender}
        for gender_type in gender_info:
            if self.id in gender_info[gender_type]:
                return int(gender_type)
            for word in gender_info[gender_type]:
                # handles compound family terms (e.g. halv-, beste-) excluding non-genetic ones
                if self.id.endswith(word) and not self.id.startswith('ste') \
                                          and not self.id.startswith('ver'):
                    self.gender = int(gender_type)
                    return int(gender_type)
                #else:
                    #self.gender = gender
        return gender

    def get_cond_val(self, entity_lem_orig, non_conditions):
        # TO DO: add NEGATION tag
        if entity_lem_orig in non_conditions:  # TO DO: add more terms?
            return 1
        return 2

    def add_condition(self, entity_lem_orig):
        """ Parses condition information.
        Distinguishes index conditions from other conditions and
        non-conditions. Only limited lexical variation handling.
        """ 
        non_conditions = ['frisk', 'gen-negativ', 'negativ', 'gravid', 'live'] # TO DO: add terms?
        index_cond_terms =  ['mutasjon', 'genbær']                     # TO DO: add terms?
        cond_val = self.get_cond_val(entity_lem_orig, non_conditions)
        if entity_lem_orig in index_cond_terms or entity_lem_orig in non_conditions:
            self.index_cond_val = cond_val            
        elif entity_lem_orig:
            self.other_conditions[entity_lem_orig] = cond_val  # other CONDITION mentions 

    def add_parents(self, pedigree):
        """ Fills mother and father attributes if still unknown (0).
        """
        for parents, children in family_relations.items():
            for child in children:
                if child == self.id:
                    mother, father = parents
                    if not self.mother:
                        self.mother = pedigree.get_member(mother)
                    if not self.father:
                        self.father = pedigree.get_member(father)  

    def add_sibling(self, pedigree, member_id, amount=1):
        for i in range(amount):
            if i:
                member_id + str(i+1)
            sibling = pedigree.get_member(member_id)
            if sibling not in self.siblings:
                self.siblings.append(sibling)

    def update_side(self, pedigree, side_lemma, amount=1):
        """ Disambiguates family relation term with parent-side information.
        Updates also siblings information accordingy. 
        """
        sides = {'mor': {'onkel':'morbror', 'tante':'moster', 'bestemor':'mormor', 'bestefar':'morfar'},
                 'far': {'onkel':'farbror', 'tante':'faster', 'bestemor':'farmor', 'bestefar':'farfar'}}
        #for parent in sides.keys():
        if 'mor' in side_lemma:
            parent = 'mor'
        elif 'far' in side_lemma:
            parent = 'far'
        else:
            parent = ''
        if parent:
            # Modifier SIDE-FAMILY
            if self.id in sides[parent]:
                self.id = sides[parent][self.id]
                #self.add_parents(pedigree) # TO DO: check if needed
                if self.id.endswith('bror') or self.id.endswith('ster'):
                    pedigree.get_member(parent).add_sibling(pedigree, self.id, amount) # TO DO: handle when e.g. 'farens bror'
                else:
                    pedigree.get_member(parent).add_parents(pedigree)
            # Related_to FAMILY-SELF/FAMILY -> separate?
            elif self.id in ['fetter', 'kusine']:
                parent_siblings = pedigree.get_member(parent).siblings
                if len(parent_siblings) == 1 and parent_siblings[0] == 'søster':
                    self.mother = pedigree.get_member(sides[parent]['tante'])
                    self.father = pedigree.get_member('onkel')
                else: # if ambiguous, brother assumed by default for parent
                    self.mother = pedigree.get_member(sides[parent]['tante'])
                    self.father = pedigree.get_member('onkel')
            else:
                print('SIDE undefined for: ', self.id)



                #    mother = pedigree.get_member(parent + 'mor') # TO DO: infer if tante or farmor
                #    # TO DO: update parent member and self's parent ids 
                #    mother.id = parent + 'mor' 
                #    pedigree.get_member(mother.id)
                #    self.mother =  mother.id
                #    father = pedigree.get_member(parent + 'mor')

    def update_relation(self, pedigree):
        pass

    def update_amount():
        pass
        # duplicate entry
        # when adding parents, if parents 0
                

class Pedigree:
    def __init__(self):
        self.id = ''
        self.other_conditions = []
        self.members = {}
        self.index_patient = None 

    def __str__(self):
        padding = '-'*30
        header = '{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}'.format('ID','FATHER','MOTHER','GENDER','AFF_STATUS','CONDITIONS')
        out = '{}\n {} pedigree members: \n{}\n{}\n'.format(padding, self.id, padding, header) 
        for member_id in self.members:
            if member_id != 'partner':
                out += self.members[member_id].__str__() + '\n'
        return out

    def save(self, format='linkage'):
        """ Save a tab-separated format with following info: 
        pedigree_id, member_id, father_ID, mother_ID, gender, affection_status, 
        # TO DO: marker_genotypes
        # TO DO: support also other formats
        """
        pass

    def get_member(self, person_id):   
        """ Add member if it does not exist yet, return
        existing member if any.
        """     
        if person_id in self.members:
            person = self.members[person_id]
        else:
            person = Person(person_id)
            self.members[person_id] = person
            person.gender = person.get_gender()
            if person.id not in ambiguous_side:
                person.add_parents(self) # TO DO: adds even if not appearing in text -> remove subsequently?
        return person

    def get_family_terms(self):
        m_to_ch = {mother:children for (mother,father),children in family_relations.items()}
        f_to_ch = {father:children for (mother,father),children in family_relations.items()}
        children = []
        for p, ch_l in family_relations.items():
            for ch in ch_l:
                if ch not in children:
                    children.append(ch)
        fam_terms = list(m_to_ch.keys()) + list(m_to_ch.keys()) + children
        return fam_terms

    def check_format():
        pass
        # ensure correct values
        # all father mother IDs also as separate row
        # no repetitions

    def populate(self, path_to_file, nlp):
        """ Creates and maps entity and relation tag information 
        to members attribute (Person instances). 
        """
        relation_info = read_relations(path_to_file)
        fam_terms = self.get_family_terms()
        for line in relation_info:
            relation, entity_tag_orig, entity_tok_orig, \
                entity_tag_target, entity_tok_target = line
            # Lemmatize
            entity_lem_target = [token.lemma_ for token in nlp(entity_tok_target)][0]
            entity_lem_orig = [token.lemma_ for token in nlp(entity_tok_orig)][0]
            print(relation, entity_tok_orig, entity_tok_target) 
            # Standardize variants 
            if entity_lem_orig in variants and entity_tok_orig == 'FAMILY':
                entity_lem_orig = variants[entity_lem_orig]
            if entity_lem_target in variants and entity_tag_target == 'FAMILY':
                entity_lem_target = variants[entity_lem_target]
            amount = 1 # TO DO: get from AMOUNT tag
            # Collect family member names and their conditions 
            if relation == 'Holder':
                if entity_tag_target == 'SELF':
                    person = self.get_member('pasient')
                elif entity_tag_target == 'FAMILY':
                    if entity_lem_target in fam_terms: # to skip other words
                        person = self.get_member(entity_lem_target)
                        if person.mother and person.father:
                            if entity_lem_target in family_relations[(person.mother.id, person.father.id)]:  #'mor', 'far'
                                person.add_sibling(self, entity_lem_target, amount)
                    # TO DO: handle that IDs not appearing in text should be 0 in output, not an id
                    # TO DO: handle 'barn' partents based on pasient gender
                    # handle 'mormor', 
                    # handle 'niese/nevø' partents based on their gender / name
                else:
                    print('Unusual target for "Holder": ' , entity_tag_target, entity_tok_target)
                if entity_tag_orig in ['CONDITION', 'EVENT']:
                    person.add_condition(entity_lem_orig)
                if entity_tag_orig == 'INDEX':
                    self.index_patient = entity_lem_target
            elif relation == 'Modifier':
                if entity_tag_orig == 'SIDE':
                    self.get_member(entity_lem_target).update_side(self, entity_lem_orig)
                # AMOUNT
                # NEG
            elif relation == 'Related_to':
                if entity_tag_target == 'FAMILY':
                    pass # TO DO: update member in pedigree (FAMILY's parents / patients' siblings etc.) 
                #if entity_tag_orig == 'FAMILY':
                #    self.get_member(entity_lem_orig).update_side(self, '')
        #for member in self.members:
        #    if member.id in ambiguous:
        #         pass # add parents based on SIDE info here?
        print(self)


    def get_linkage_format(data_folder):
        # populate(self, path_to_file, nlp)
        # create each line from info in Person (tab sep) 
        pass

"""
Ongoing:

To do:
- FAMILY:   
    mor/far for halvbror
    sibling addition handled for: patient and mor/far (not others)
- pronouns
    use for updating info on last mentioned Person.id
    use for disambiguating gender for genderless FAMILY / SELF (e.g. barn)
- NEGATION
    use to add/modify info in Person.conditions  -> uncertainty AND negation!
- add missing family terms: søskenbarn, sønnesønn, oldemor, oldefar, forelder
- move global vars not used in Person to Pedigree attribs?
- process relations in a certain order?
- check if 'farens bror' annotated as Related_to


"""

#Info:
# https://www.broadinstitute.org/haploview/input-file-formats
# http://csg.sph.umich.edu/abecasis/merlin/tour/input_files.html

