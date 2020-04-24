
import os

global variants
global family_relations
global sides
global ambiguous_side
global gender_info

variants = {'broder': 'bror', 
            'fader':'far',
            'mor' : 'moder', 
            'fett':'fetter',     # fixes UDPipe tokenization issue
            'Pasient': 'pasient'}

family_relations = {
    ('partner', 'pasient') : ['datter', 'sønn', 'barn'],
    ('mor', 'far') : ['pasient', 'søster', 'halvsøster', 'bror', 'halvbror'],
    ('mormor', 'morfar') : ['mor', 'tante', 'onkel', 'moster', 'morbror'],
    ('farmor', 'farfar') : ['far', 'tante', 'onkel', 'faster', 'farbror'],
    ('faster', 'onkel') : ['kusine', 'fetter'],
    ('moster', 'onkel') : ['kusine', 'fetter'],
    ('tante', 'farbror') : ['kusine', 'fetter'],
    ('tante', 'morbror') : ['kusine', 'fetter'],
    ('søster', 'svigerbror') : ['niese', 'nevø'],
    ('svigersøster', 'bror') : ['niese', 'nevø']}

sides = {'mor': {'onkel':'morbror', 'tante':'moster', 
                 'bestemor':'mormor', 'bestefar':'morfar'},
         'far': {'onkel':'farbror', 'tante':'faster', 
                 'bestemor':'farmor', 'bestefar':'farfar'}}

ambiguous_side = ['bestemor', 'bestefar','tante', 'onkel', 'kusine', 'fetter', 'niese', 'nevø']
gender_info = {'2' : ['mor', 'søster', 'datter', 'tante', 'faster', 'moster',
                      'niese', 'kone', 'hustru', 'kusine'],
               '1' : ['far', 'bror', 'sønn', 'onkel', 'farbror', 'morbror', 
                      'nevø', 'man', 'husbond', 'fetter'],
               '0' : ['barn', 'søsken', 'forelder']}

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
                continue
            elif line == "\n":
                continue
            elif line.startswith("# text =  "):
                sent = line[10:-1]
            else:
                line_elem = line.strip().split("\t")
                relation = line_elem[1]
                orig_tag, l_ix_orig, r_ix_orig = line_elem[2].split(",")
                orig_token = sent[int(l_ix_orig):int(r_ix_orig)]
                target_tag, l_ix_target, r_ix_target = line_elem[3].split(",")
                target_token = sent[int(l_ix_target):int(r_ix_target)]
                relation_info.append([relation, orig_tag, orig_token, 
                                      target_tag, target_token])
    return relation_info

class Person:
    def __init__(self, person_id):
        self.id = person_id
        self.father = 0             # 0=unknown
        self.mother = 0             # 0=unknown
        self.siblings = []
        self.side = None            # 'far' or 'mor'
        self.gender = None          # 0=unknown / 1=male / 2=female
        self.phenotype = 0          # 0=unknown / 1=negative / 2=positive
        self.conditions = {}
    
    def __str__(self):
        if self.father:
            father = self.father.id
        else:
            father = self.father
        if self.mother:
            mother = self.mother.id
        else:
            mother = self.mother
        out = '{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}'.format(self.id, father, mother, 
                                    self.gender, self.phenotype, '\t'.join(['{}'.format(cond) 
                                                for (cond, val) in self.conditions.items()]))
        return out

    def get_gender(self):
        """ Returns numeric value corresponding to gender 
        (0 = unknown, 1 = male, 2 = female).
        E.g. 0: forelder, sysken, tvilling, barn, kusin
        """
        gender = 0
        for gender_type in gender_info:
            if self.id in gender_info[gender_type]:
                return int(gender_type)
            for word in gender_info[gender_type]:
                # handles compound family terms (e.g. halv-, beste-) excluding non-genetic ones
                if self.id.endswith(word) and not self.id.startswith('ste') \
                                          and not self.id.startswith('ver'):
                    self.gender = int(gender_type)
                    return int(gender_type)
        return gender

    def get_cond_val(self, orig_lemma, non_conditions):
        # TO DO: add NEGATION tag
        if orig_lemma in non_conditions:  
            return 1
        return 2

    def add_condition(self, orig_lemma):
        """ Parses condition information.
        Distinguishes index conditions from other conditions and
        non-conditions. Only limited lexical variation handling.
        """ 
        non_conditions = ['frisk', 'gen-negativ', 'negativ', 'gravid', 'live']  # TO DO: add terms?
        index_cond_terms =  ['mutasjon', 'genbær']                              # TO DO: add terms?
        cond_val = self.get_cond_val(orig_lemma, non_conditions)
        if orig_lemma in index_cond_terms or orig_lemma in non_conditions:
            self.phenotype = cond_val            
        elif orig_lemma:
            self.conditions[orig_lemma] = cond_val  # medical issues from CONDITION 

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
            #print(self.id, member_id)
            if i:
                member_id = member_id + str(i+1)
            if member_id != self.id: # to exclude oneself from list of children
                sibling = pedigree.get_member(member_id)
                #print(sibling.id)
                if sibling not in self.siblings:
                    self.siblings.append(sibling)
            #print('SIB',pedigree.members.keys())
                

class Pedigree:
    def __init__(self):
        self.id = ''
        self.conditions = []
        self.members = {}
        self.disamb_members = {}
        self.index_patient = None 

    def __str__(self):
        padding = '-'*30
        header = '{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}'.format(
                'ID','FATHER','MOTHER','GENDER','PHENOTYPE','CONDITIONS')
        out = '{}\n {} pedigree members: \n{}\n{}\n'.format(padding, self.id, padding, header) 
        for member_id in self.members:
            if member_id != 'partner':
                out += self.members[member_id].__str__() + '\n'
        return out

    def save(self, format='linkage'):
        """ Save a tab-separated format with following info: 
        pedigree_id, member_id, father_ID, mother_ID, gender, phenotype
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
                person.add_parents(self)
        return person

    def normalize_lemma(self, orig_lemma, orig_tag, target_lemma, target_tag):
        # Standardize variants 
        if orig_lemma in variants and orig_tag in ['FAMILY', 'SELF']:
            orig_lemma = variants[orig_lemma]
        if target_lemma in variants and target_tag in ['FAMILY', 'SELF']:
            target_lemma = variants[target_lemma]
        # Map to disambiguated if any
        if orig_lemma in self.disamb_members:
            orig_lemma = self.disamb_members[orig_lemma]
        elif target_lemma in self.disamb_members:
            target_lemma = self.disamb_members[person.id]
        return(orig_lemma, target_lemma)

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

    def update_side(self, person, side_lemma, amount=1):
        """ Disambiguates family relation term with parent-side information.
        Updates also siblings information accordingy. 
        Handles Modifier relation with SIDE + FAMILY entities.
        """
        if 'mor' in side_lemma:
            parent = 'mor'
        elif 'far' in side_lemma:
            parent = 'far'
        else:
            parent = ''
        if parent:
            person.side = parent
            print(person.id, person.side)
            # Modifier SIDE-FAMILY
            if person.id in sides[parent]:
                disamb_fam = sides[parent][person.id]
                # make a copy of Person with disabiguated SIDE
                self.members[disamb_fam] = self.members[person.id]  
                self.disamb_members[person.id] = disamb_fam
                del self.members[person.id]
                self.members[disamb_fam].id = disamb_fam
                self.members[disamb_fam].add_parents(self)
                if disamb_fam.endswith('bror') or disamb_fam.endswith('ster'):
                    self.get_member(parent).add_sibling(self, disamb_fam, amount)
                else:
                    self.get_member(parent).add_parents(self)             
        else:
            print('Unknown SIDE: ', side_lemma)

    def update_related(self, orig_lemma, target_tag, target_lemma):
        # Related_to FAMILY-SELF/FAMILY -> separate?
        person = self.get_member(orig_lemma)
        if target_tag == 'SELF': 
            print(orig_lemma, person.side)
            if person.id in ['fetter', 'kusine'] and person.side:
                parent_siblings = self.get_member(person.side).siblings
                if len(parent_siblings) == 1: 
                    if parent_siblings[0] == 'søster':
                        person.mother = self.get_member(sides[person.side]['tante'])
                        person.father = self.get_member('onkel')
                    else:
                        person.mother = self.get_member('tante')
                        person.father = self.get_member(sides[person.side]['onkel'])
                else:
                    print('Ambiguous Related_to: multiple parent siblings')
            elif person.id in ['nevø', 'niese']:
                patient_siblings = self.get_member(target_lemma).siblings
                if len(patient_siblings) == 1: 
                    if parent_siblings[0] == 'søster':
                        person.mother = self.get_member('søster')
                        person.father = self.get_member('svigerbror')
                    else:
                        person.mother = self.get_member('svigersøster')
                        person.father = self.get_member('bror')
                else:
                    print('Ambiguous Related_to: multiple patient siblings') 
        elif target_tag == 'FAMILY' and person.side:
            # family term not relative to SELF (patient) TO DO: modify name to reflect relative to patient
            print('Related_to not handles between: ', orig_lemma, target_lemma)

    def update_amount():
        pass
        # duplicate entry
        # when adding parents, if parents 0


    def populate(self, path_to_file, nlp):
        """ Creates and maps entity and relation tag information 
        to members attribute (Person instances). 
        """
        relation_info = read_relations(path_to_file)
        fam_terms = self.get_family_terms()
        print('{:<15}{:<15}{:<13}{:<15}{:<10}'.format('relation'.upper(), 'orig_lemma'.upper(), '(orig_tag)'.upper(), 
                                            'target_lemma'.upper(), '(target_tag)'.upper()))
        print('-'*65)
        for line in relation_info:
            relation, orig_tag, orig_token, \
                target_tag, target_token = line
            
            # Lemmatize
            target_lemma = [token.lemma_ for token in nlp(target_token)][0]
            orig_lemma = [token.lemma_ for token in nlp(orig_token)][0]
            orig_lemma, target_lemma = self.normalize_lemma(orig_lemma, orig_tag, target_lemma, target_tag)
            print('{:<15}{:<15}{:<13}{:<15}{:<10}'.format(relation, orig_lemma, '('+orig_tag+')', target_lemma, '('+target_tag+')'))
            
            amount = 1 # TO DO: get from AMOUNT tag
            # Collect family member names and their conditions 
            if relation == 'Holder':
                if target_tag == 'SELF':
                    person = self.get_member('pasient')
                    self.disamb_members[orig_lemma] = 'pasient'
                elif target_tag == 'FAMILY':
                    if target_lemma in fam_terms: # to skip any other word
                        person = self.get_member(target_lemma)
                        if person.mother and person.father:
                            if target_lemma in family_relations[(person.mother.id, person.father.id)]:  #'mor', 'far'
                                person.add_sibling(self, target_lemma, amount)
                else:
                    print('Unusual target for "Holder": ' , target_tag, target_token)
                if orig_tag in ['CONDITION', 'EVENT']:
                    person.add_condition(orig_lemma)
                if orig_tag == 'INDEX':
                    self.index_patient = target_lemma
            elif relation == 'Modifier':
                if orig_tag == 'SIDE':
                    self.update_side(self.get_member(target_lemma), orig_lemma)
                # AMOUNT
                # NEG
            elif relation == 'Related_to':
                self.update_related(orig_lemma, target_tag, target_lemma)
            print('\n')
        print(self)


"""
Do next:
- remove pasient from conditions
- handle other terms (ambiguous and non 'farfar hadde 2 brødre') etc to related to 

Other to dos:
- FAMILY:   
    mor/far for halvbror
    sibling addition handled for: patient and mor/far (not others)
    family terms not always relative to SELF (pasient) e.g. text2 'Farfar hadde to brødre' 'farens bror'
- pronouns
    use for updating info on last mentioned Person.id
    use for disambiguating gender for genderless FAMILY / SELF (e.g. barn)
- NEGATION
    use to add/modify info in Person.conditions  -> uncertainty AND negation!
- add missing family terms: søskenbarn, sønnesønn, oldemor, oldefar, forelder
- move global vars not used in Person to Pedigree attribs?
- process relations in a certain order?
- check if 'farens bror' annotated as Related_to
- add pedigree ID in final LINKAGE format
- switch defaults to unknown
- marker_genotypes after phenotype column
- remove superflous: parents added even if not appearing in text -> remove subsequently when not used


Done

- move update_side to Pedigree
- duplicate entries
- move relation to separate function

"""


