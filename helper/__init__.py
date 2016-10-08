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

    def page(self):
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

    def page(self):
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

class Proxy (object):
    def __init__(self, type):
        self.type = type
        self.data = None

        self.spells = None
        self.classes = None

        self.folder = None
        self.sources = None

    def __call__(self, datafolder=None, sources=None):
        self.folder = datafolder
        self.sources = sources

    def filter(self, f=None):
        if self.data is None:
            self.data = self.type(self.folder, self.sources)
            if self.spells is not None:
                self.data.set_spell_list(self.spells)
            if self.classes is not None:
                self.data.set_class_list(self.classes)
        if f is None:
            return self.data
        else:
            return self.data.filter(f)

    def set_spell_list(self, spell_list):
        if isinstance(spell_list, Proxy):
            spell_list = spell_list.filter()
        self.spells = spell_list
        if self.data is not None:
            self.data.set_spell_list(self.spells)

    def set_class_list(self, class_list):
        if isinstance(spell_list, Proxy):
            class_list = class_list.filter()
        self.classes = class_list
        if self.data is not None:
            self.data.set_class_list(self.classes)

datafolder = None
sources_order = None
class_list = Proxy(classes.Classes)
race_list = Proxy(races.Races)
document_list = Proxy(Documents)
background_list = Proxy(backgrounds.Backgrounds)
spell_list = Proxy(spells.Spells)
feat_list = Proxy(feats.Feats)
epicboon_list = Proxy(feats.EpicBoons)
monster_list = Proxy(monsters.Monsters)
magicitem_list = Proxy(magicitems.MagicItems)
weapon_list = Proxy(items.Weapons)
armor_list = Proxy(items.Armors)
optionalrule_list = Proxy(OptionalRules)
item_list = Proxy(items.Items)

def init(folder=None):
    global datafolder, sources_order, weapon_list, armor_list, optionalrule_list, item_list

    if folder is None:
        folder = 'data'
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

    for item in l:
        item(datafolder, sources_order)

    for item in l:
        item.set_spell_list(spell_list)
    spell_list.set_class_list(class_list)
