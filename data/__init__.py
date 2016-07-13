import helper

helper.init()

def f(a):
    return not a.startswith('UA-')

def final_changes(d):
    d['name'] = 'Official'

# ----#-

sources = helper.archiver.load('data/sources.json')
sources = list(filter(f, sources))

d = {}

for name, set in [('class', helper.class_list), ('race', helper.race_list)]:
    d[name] = {}
    for key in set:
        data = {}
        for sub in set[key]['sub' + name]:
            #if set[key]['+'] not in sources:
            #    data[sub] = False
            if set[key]['sub' + name][sub]['+'] in sources:
                data[sub] = True
            else:
                data[sub] = False
        if len(data):
            d[name][key] = data
        else:
            d[name][key] = set[key]['+'] in sources

for name, set in [
    ('background', helper.background_list),
    ('spell', helper.spell_list),
    ('feat', helper.feat_list),
    ('epicboon', helper.epicboon_list),
    ('magicitem', helper.magicitem_list),
    ('weapon', helper.weapon_list),
    ('armor', helper.armor_list),
    ('optionalrule', helper.optionalrule_list)]:
    d[name] = {}
    for key in set:
        d[name][key] = set[key]['+'] in sources

final_changes(d)

helper.archiver.save(d, 'data/filter/official.json')
