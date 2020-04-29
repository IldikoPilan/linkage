from constants import *

class Person:
    def __init__(self, person_id):
        self.id = person_id
        self.father = 0             # 0=unknown
        self.mother = 0             # 0=unknown
        self.siblings = []
        self.side = None            # 'far' or 'mor'
        self.amount = 1
        self.gender = 3             # 1=male / 2=female / 3=unknown
        self.phenotype = 'NA'       # NA=unknown / 0=negative / 1=positive
        self.conditions = []
    
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
                                    self.gender, self.phenotype, ', '.join(self.conditions))
        return out

    def get_gender(self):
        """ Updates gender attribute with a numeric value based on family term. 
        (1 = male, 2 = female, 3 = unknown).
        E.g. 3: forelder, sysken, barn
        """
        for gender_type in gender_info:
            if self.id in gender_info[gender_type]:
                self.gender = int(gender_type)
            for word in gender_info[gender_type]:
                # handles compound family terms (e.g. halv-, beste-) excluding non-genetic ones
                if self.id.endswith(word) and not self.id.startswith('ste') \
                                          and not self.id.startswith('ver'):
                    self.gender = int(gender_type)
        
    def add_condition(self, orig_lemma):
        """ Parses condition information.
        Distinguishes index conditions from other conditions and
        non-conditions. Only limited amount of words handled.
        """ 
        if orig_lemma in index_cond_terms:
            self.phenotype = 1
        elif orig_lemma in non_conditions:  
            self.phenotype = 0          
        else:
            self.conditions.append(orig_lemma) # diverse medical issues from CONDITION 

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

    def add_sibling(self, pedigree, member_id): 
        """ Adds a sibling.
        """
        if member_id != self.id: # to exclude oneself from list of children
            sibling = pedigree.get_member(member_id)
            if sibling not in self.siblings:
                self.siblings.append(sibling)
                