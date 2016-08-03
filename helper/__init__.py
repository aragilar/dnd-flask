import sys
import os
import re
import collections

from . import archiver
from . import utils
from . import classes
from . import races
from . import backgrounds
from . import spells
from . import feats
from . import monsters
from . import magicitems
from . import items

slug = utils.slug

class Documentation (utils.Base):
    description = ''
    
    def __init__(self, data):
        self.name = data[0].lstrip('#').strip()
        self.source = 'FREE'
        d = ''.join(data[0:])
        d = utils.convert(d)
        d = utils.get_details(d, splttag='h1')
        self.description = d
    
    def __str__(self):
        html = self.description
        html = '<div>\n%s</div>\n' % html
        return html

class Documents (utils.Group):
    type = Documentation
    
    docs = [
        'preface',
        'introduction',
        'character-creation',
        'personality',
        'equipment',
        'customization',
        'abilities',
        'adventuring',
        'combat',
        'conditions',
        'gods',
        'planes',
    ]

    def __init__(self, folder=None, sources=None):
        super().__init__()
        if folder:
            folder = os.path.join(folder, 'documentation')
            for item in self.docs:
                item = os.path.join(folder, item + '.md')
                if os.path.exists(item):
                    with open(item, 'r', encoding='utf-8') as f:
                        item = f.readlines()
                    if item:
                        item = self.type(item)
                        self.add(item)
    
    def sort(self, key=None):
        pass

class OptionalRule (utils.Base):
    description = ''

    def __init__(self, data):
        self.name = data[1].lstrip('#').strip()
        self.source = data[0].strip()
        d = ''.join(data[1:])
        d = utils.convert(d)
        d = utils.get_details(d, splttag='h1')
        self.description = d

    def __str__(self):
        html = self.description
        html = '<div>\n%s</div>\n' % html
        return html

class OptionalRules (utils.Group):
    type = OptionalRule

    def __init__(self, folder=None, sources=None):
        super().__init__()
        if folder:
            folder = os.path.join(folder, 'optionalrule')
            if os.path.exists(folder):
                for item in sorted(os.listdir(folder)):
                    item = os.path.join(folder, item)
                    if os.path.exists(item) and item.endswith('.md'):
                        with open(item, 'r', encoding='utf-8') as f:
                            item = f.readlines()
                        if len(item) > 1:
                            item = self.type(item)
                            
                            if sources is None or item.source in sources:
                                self.add(item)

datafolder = None
sources_order = None
class_list = classes.Classes()
race_list = races.Races()
document_list = Documents()
background_list = backgrounds.Backgrounds()
spell_list = spells.Spells()
feat_list = feats.Feats()
epicboon_list = feats.EpicBoons()
monster_list = monsters.Monsters()
magicitem_list = magicitems.MagicItems()
weapon_list = items.Weapons()
armor_list = items.Armors()
optionalrule_list = OptionalRules()
item_list = items.Items()

def init(folder='data'):
    global datafolder, sources_order, weapon_list, armor_list, optionalrule_list, item_list

    datafolder = folder

    sources_order = archiver.load(os.path.join(datafolder, 'sources.json'))
    
    l = [
        class_list,
        race_list,
        document_list,
        background_list,
        spell_list,
        feat_list,
        epicboon_list,
        monster_list,
        magicitem_list,
        weapon_list,
        armor_list,
        optionalrule_list,
        item_list,
    ]
    
    utils.asyncmap(lambda a: a.__init__(datafolder, sources_order), l)
    for item in l:
        item.sort(lambda a: a.name)
        if item in (class_list, race_list):
            item.sort(key=lambda a: sources_order.index(a.source))
            item.sort(key=lambda a: a.index)
        item.set_spell_list(spell_list)
    spell_list.set_class_list(class_list)
