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
from . import magicitems
from . import items
slug = utils.slug

class OptionalRule (utils.Base):
    description = ''

    def __init__(self, data):
        self.name = data[1].lstrip('#').strip()
        self.source = data[0].strip()
        self.description = ''.join(data[1:])

    def __str__(self):
        html = self.description
        html = utils.convert(html)
        html = utils.get_details(html)
        html = '<div>\n%s</div>\n' % html
        return html

class OptionalRules (utils.Group):
    type = OptionalRule

    def __init__(self, folder=None, sources=None):
        super().__init__()
        if folder:
            folder = os.path.join(folder, 'optionalrule')
            for item in sorted(os.listdir(folder)):
                item = os.path.join(folder, item)
                if os.path.exists(item) and item.endswith('.md'):
                    with open(item, 'r') as f:
                        item = f.readlines()
                    if len(item) > 1:
                        item = self.type(item)
                        
                        if sources is None or item.source in sources:
                            self.add(item)

datafolder = None
sources_order = None
class_list = classes.Classes()
race_list = races.Races()
background_list = backgrounds.Backgrounds()
spell_list = spells.Spells()
feat_list = feats.Feats()
epicboon_list = feats.EpicBoons()
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
        background_list,
        spell_list,
        feat_list,
        epicboon_list,
        magicitem_list,
        weapon_list,
        armor_list,
        optionalrule_list,
        item_list,
    ]
    
    utils.asyncmap(lambda a: a.__init__(datafolder, sources_order), l)
    for item in l:
        item.sort(lambda a: a.name)
        if type(item) in (classes.Classes, races.Races):
            item.sort(key=lambda a: sources_order.index(a.source))
            item.sort(key=lambda a: a.index)
        item.set_spell_list(spell_list)

def load(folder, sources=sources_order):
    global datafolder
    if datafolder is None:
        if sources is None:
            return None
        else:
            return {}
    path = os.path.join(datafolder, folder) 
    if folder.endswith('.md'):
        try:
            with open(os.path.join(datafolder, 'documentation', folder)) as f:
                d = f.read()
        except IOError:
            d = None
    elif not os.path.exists(path):
        d = None
    elif folder.endswith('.json'):
        try:
            d = archiver.load(path)
        except IOError:
            d = None
    else:
        try:
            with open(path) as f:
                d = f.read()
        except IOError:
            d = None
    return d

# ----#-

def class2html(c, keys=None):
    cs = class_list.filter(keys)
    if c in cs:
        return str(cs[c])
    else:
        return None

def race2html(r, keys=None):
    rs = race_list.filter(keys)
    if r in rs:
        return str(rs[r])
    else:
        return None

def background_page(keys=None):
    bgs = background_list.filter(keys)
    if bgs:
        return bgs.page(load)
    else:
        return None

def spell_page(keys=None):
    sps = spell_list.filter(keys)
    if sps:
        return sps.page(class_list.filter(keys), load)
    else:
        return None

def spell2html(s, keys=None):
    sps = spell_list.filter(keys)
    if s in sps:
        return "<div>\n%s</div>\n" % str(sps[s])
    else:
        return None

def magicitem_page(keys=None):
    mis = magicitem_list.filter(keys)
    if mis:
        return mis.page(load)
    else:
        return None

def magicitem2html(m, keys=None):
    mis = magicitem_list.filter(keys)
    if m in mis:
        return "<div>\n%s</div>\n" % str(mis[m])
    else:
        return None

def feat_page(keys=None):
    fs = feat_list.filter(keys)
    if fs:
        return fs.page(load)
    else:
        return None

def boon_page(keys=None):
    bs = epicboon_list.filter(keys)
    if bs:
        return bs.page(load)
    else:
        return None

def item_page(keys=None):
    wps = weapon_list.filter(keys)
    ams = armor_list.filter(keys)
    its = item_list.filter(keys)
    if wps or ams or its:
        return items.main(wps, ams, its, load)
    else:
        return None

def optionalrule_page(key, keys=None):
    rules = optionalrule_list.filter(keys)
    if key in rules:
        return str(rules[key])
    else:
        return None

def documentation(page):
    page += '.md'
    data = load(page)
    if data is not None:
        html = utils.convert(data)
        html = utils.get_details(html)
        html = '<div>\n%s</div>\n' % html
        return html
    else:
        return None
