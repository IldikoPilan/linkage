
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


        
