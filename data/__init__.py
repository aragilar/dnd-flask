import helper

helper.init()

# ----#-

def main(type):
    sources = helper.archiver.load('data/sources.json')
    sources = list(filter(type.sources, sources))
    
    d = {}
    
    for name, set in [('class', helper.class_list), ('race', helper.race_list)]:
        d[name] = {}
        for item in set.values():
            data = {}
            for sub in item.children.values():
                if sub.source in sources:
                    data[sub.name] = True
                else:
                    data[sub.name] = False
            if len(data):
                d[name][item.name] = data
            else:
                d[name][item.name] = item.source in sources
    
    for name, set in [
        ('background', helper.background_list),
        ('spell', helper.spell_list),
        ('feat', helper.feat_list),
        ('epicboon', helper.epicboon_list),
        ('magicitem', helper.magicitem_list),
        ('weapon', helper.weapon_list),
        ('armor', helper.armor_list),
        ('item', helper.item_list),
        ('optionalrule', helper.optionalrule_list)]:
        d[name] = {}
        for item in set.values():
            d[name][item.name] = item.source in sources
    
    type.final_pass(d)
    
    d['name'] = type.name
    
    helper.archiver.save(d, 'data/filter/%s.json' % helper.slug(type.name))

#############################################

class base (object):
    name = 'base'
    
    @staticmethod
    def sources(source):
        return True
    
    @staticmethod
    def final_pass(d):
        pass

class phb (base):
    name = 'PHB'
    
    @staticmethod
    def sources(a):
        return a in ['FREE', 'PHB']

class core (base):
    name = 'Core'
    
    @staticmethod
    def sources(a):
        return a in ['FREE', 'PHB', 'MM', 'DMHB']

class official (base):
    name = 'Official'
    
    @staticmethod
    def sources(a):
        return not a.startswith('UA-')

class ua (base):
    name = 'Unearthed Arcana'
    
    @staticmethod
    def sources(a):
        return a.startswith('UA-')

class modern (base):
    name = 'Modern'
    
    @staticmethod
    def sources(a):
        ret = True
        if a.startswith('UA-') and a != 'UA-MODERN':
            ret = False
        return ret
    
    @staticmethod
    def final_pass(d):
        keep = [
            'Action Options',
            'Explosives',
            'Firearms',
            'Hitting Cover',
            'Injuries',
            'Massive Damage',
            'Modern Rules',
            'Morale'
        ]
        op = d['optionalrule']
        for key in op:
            op[key] = key in keep
        
        d['race']['Warforged'] = True

class feyfall (base):
    name = 'Feyfall'
    
    @staticmethod
    def sources(a):
        ret = not a.startswith('UA-')
        if a in ['UA-RUNESCRIBE']:
            ret = True
        return ret
    
    @staticmethod
    def final_pass(d):
        keep = [
            'Action Options',
            'Hitting Cover',
            'Injuries',
            'Massive Damage',
            'Morale',
            'Spell Points',
        ]
        op = d['optionalrule']
        for key in op:
            op[key] = key in keep
        
        keep = [
            'Shifter',
            'Warforged',
            'Minotaur',
        ]
        r = d['race']
        for key in keep:
            if isinstance(r[key], bool):
                r[key] = True
            else:
                for sub in r[key]:
                    r[key][sub] = True
        
        d['background']['Haunted One'] = False
        
        d['class']['Ranger']['Deep Stalker'] = True
        #d['class']['Sorcerer']['Favored Soul'] = True

all = [phb, core, official, ua, modern, feyfall]
