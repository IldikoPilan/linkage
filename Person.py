from constants import *

class Person:
    def __init__(self, person_id):
        self.id = person_id
        self.father = 0             # 0=unknown
        self.mother = 0             # 0=unknown
        self.siblings = []
        self.side = None            # 'far' or 'mor'
        self.amount = 1
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
        index_cond_terms =  ['mutasjon', 'genbær', 'syk']                       # TO DO: add terms?
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
                        pedigree.auto_members.append(mother)
                    if not self.father:
                        self.father = pedigree.get_member(father)  
                        pedigree.auto_members.append(father)

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
                