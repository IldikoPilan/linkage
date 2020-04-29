
import os
import codecs
from utils import read_relations
from Person import Person
from constants import *

class Pedigree:
    def __init__(self):
        self.id = ''
        self.conditions = []
        self.members = {}
        self.disamb_members = {}
        self.index_patient = None # not required for LINKAGE, used to set phenotype value to 1 
        self.patient_gender = 0
        self.auto_members = []

    def __str__(self):
        padding = '-'*30
        header = '{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}\t{:<10}'.format(
                'ID','FATHER','MOTHER','GENDER','PHENOTYPE','CONDITIONS')
        out = '{}\n {} pedigree members: \n{}\n{}\n'.format(padding, self.id, padding, header) 
        for member_id in self.members:
            if member_id != 'partner':
                out += self.members[member_id].__str__() + '\n'
        return out

    def save(self, path_to_file, out_folder, format='linkage'):
        """ Save a tab-separated format with following info: 
        pedigree_id, member_id, father_ID, mother_ID, gender, phenotype
        """
        print(self.id_mapping)
        self.members['pasient'].gender = 1 # dev version fix
        self.members['partner'].gender = 2 # dev version fix
        out_f = os.path.split(path_to_file)[1].split('.')[0]+'.ped'
        out = '"id" "fid" "mid" "sex" "aff" \n'
        for name, member in self.members.items():
            mother = 0
            if member.mother:
                mother = self.id_mapping.get(member.mother.id)
            father = 0
            if member.father:
                father = self.id_mapping.get(member.father.id)
            member_info = "{} {} {} {} {}\n".format(self.id_mapping[name], father, mother,
                                                    member.gender, member.phenotype)
            out += member_info
        out += '\n'
        with codecs.open(os.path.join(out_folder, out_f), 'w', 'utf-8') as f:
            f.write(out)


    def get_member(self, person_id):   
        """ Add member if it does not exist yet, return
        existing member if any.
        """     
        if person_id in self.members:
            person = self.members[person_id]
        else:
            person = Person(person_id)
            self.members[person_id] = person
            person.get_gender()
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
        if target_lemma in self.disamb_members:
            target_lemma = self.disamb_members[target_lemma]
        return(orig_lemma, target_lemma)

    def get_family_terms(self):
        """ Returns a list of family terms.
        """ 
        m_to_ch = {mother:children for (mother,father),children in family_relations.items()}
        f_to_ch = {father:children for (mother,father),children in family_relations.items()}
        children = []
        for p, ch_l in family_relations.items():
            for ch in ch_l:
                if ch not in children:
                    children.append(ch)
        fam_terms = list(m_to_ch.keys()) + list(m_to_ch.keys()) + children
        return fam_terms

    def get_patient_gender(self, lemma, tag):
        """ Infers patient's gender based on pronouns tagged as SELF
        if it hasn't been inferred yet.
        Does not assume heterosexual couples (i.e. no inference from partner's gender).
        """
        if not self.get_member('pasient').gender:
            if lemma in ['han', 'hans']:
                self.patient_gender = 1
            elif lemma in ['hun', 'hennes']:            
                self.patient_gender = 2

    def check_format():
        pass
        # ensure correct values
        # all father mother IDs also as separate row
        # no repetitions

    def copy_member_info(self, orig_lemma, new_member_id):
        self.members[new_member_id].mother = self.members[orig_lemma].mother
        self.members[new_member_id].father = self.members[orig_lemma].father
        self.members[new_member_id].gender = self.members[orig_lemma].gender
        self.members[new_member_id].siblings = self.members[orig_lemma].siblings
        self.members[new_member_id].siblings.append(self.members[orig_lemma]) # TO DO: check whether overgenerates
        self.members[orig_lemma].siblings.append(self.members[new_member_id]) # TO DO: check whether overgenerates

    def update_side(self, person, side_lemma):
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
                    self.get_member(parent).add_sibling(self, disamb_fam)
                else:
                    self.get_member(parent).add_parents(self)
            self.update_amount(person.id, 'FAMILY', person.amount)             
        else:
            print('Unknown SIDE: ', side_lemma)

    def update_related(self, orig_lemma, target_tag, target_lemma):
        # Related_to FAMILY-SELF/FAMILY -> separate?
        person = self.get_member(orig_lemma)
        if target_tag == 'SELF': 
            self.get_patient_gender(target_lemma, target_tag)
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
            self.update_amount(person.id, 'FAMILY', person.amount) 
        elif target_tag == 'FAMILY': 
            # family term not relative to SELF (patient) TO DO: modify name to reflect relative to patient
            print('Related_to not handled between: ', orig_lemma, target_lemma)        

    def update_amount(self, orig_lemma, orig_tag, target_lemma, target_tag='AMOUNT'):
        """ Multiplies a member type based on AMOUNT and copies information
            available up to that point.
            Handles Modifier relation with FAMILY - AMOUNT (regardless of entity order). 
        """ 
        # Handle any entity tag order
        if orig_tag == 'AMOUNT':
            amount_term = orig_lemma
        else:
            amount_term = target_lemma
        if orig_tag == 'FAMILY':
            family_term = orig_lemma    
        elif target_tag == 'FAMILY':
            family_term = target_lemma
        else:
            family_term = ''
            
        # Get amount
        if amount_term in amounts:
            amount = amounts[amount_term]
        elif str(amount_term).isdigit():
            amount = amount_term
        else:
            print('Unknown amount: ', amount_term)
            amount = 1

        # Multiply members based on AMOUNT
        if family_term:
            self.get_member(family_term).amount = amount
            for i in range(amount):
                if i:
                    new_member_id = family_term + str(i+1)
                    new_member = self.get_member(new_member_id)
                    self.copy_member_info(family_term, new_member_id)
        else:
            pass 
            # TO DO: handle CONDITION / EVENT

    def convert_ids(self):
        self.id_mapping = {}
        for ix, (name, info) in enumerate(self.members.items()):
            self.id_mapping[name] = ix+1
        # TO DO: finish

    def populate(self, path_to_file, nlp, out_dir):
        """ Creates and maps entity and relation tag information 
        to members attribute (Person instances). 
        """
        relation_info = read_relations(path_to_file)
        fam_terms = self.get_family_terms()
        print('{:<15}{:<15}{:<13}{:<15}{:<10}'.format('relation'.upper(), 'orig_lemma'.upper(), 
                                                      '(orig_tag)'.upper(), 'target_lemma'.upper(), 
                                                      '(target_tag)'.upper()))
        print('-'*65)
        for line in relation_info:
            relation, orig_tag, orig_token, \
                target_tag, target_token = line
            
            # Lemmatize
            target_lemma = [token.lemma_ for token in nlp(target_token)][0]
            orig_lemma = [token.lemma_ for token in nlp(orig_token)][0]
            orig_lemma, target_lemma = self.normalize_lemma(orig_lemma, orig_tag, 
                                                            target_lemma, target_tag)
            print('{:<15}{:<15}{:<13}{:<15}{:<10}'.format(relation, orig_lemma, 
                                                          '('+orig_tag+')', target_lemma, 
                                                          '('+target_tag+')'))
            # Collect family member names and their conditions 
            if relation == 'Holder':
                if target_tag == 'SELF':
                    person = self.get_member('pasient')
                    self.disamb_members[target_lemma] = 'pasient'
                    self.get_patient_gender(target_lemma, target_tag)
                elif target_tag == 'FAMILY':
                    if target_lemma in fam_terms: # to skip any other word
                        person = self.get_member(target_lemma)
                        if person.mother and person.father:
                            if target_lemma in family_relations[(person.mother.id, person.father.id)]: 
                                person.add_sibling(self, target_lemma)
                else:
                    print('Unusual target for "Holder": ' , target_tag, target_token)
                if orig_tag in ['CONDITION', 'EVENT']:
                    person.add_condition(orig_lemma)
                if orig_tag == 'INDEX':
                    self.index_patient = target_lemma
            elif relation == 'Modifier':
                if orig_tag == 'SIDE':
                    self.update_side(self.get_member(target_lemma), orig_lemma)
                elif target_tag == 'AMOUNT' or orig_tag == 'AMOUNT':
                    self.update_amount(orig_lemma, orig_tag, target_lemma, target_tag)
                # NEG
            elif relation == 'Related_to':
                self.update_related(orig_lemma, target_tag, target_lemma)
            print('\n')
        self.members['pasient'].gender = self.patient_gender
        if self.index_patient in self.members:
            self.members[self.index_patient].phenotype = 1
        self.convert_ids()
        self.save(path_to_file, out_dir)
        print(self)
        