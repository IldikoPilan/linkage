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