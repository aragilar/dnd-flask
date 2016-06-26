#!/usr/bin/env python2

import os
import re
import archiver
import utils
import classes
import races
import backgrounds
import spells
import feats
import magicitems
import items

datafolder = None
sources_order = None
class_list = None
race_list = None
background_list = None
spell_list = None
feat_list = None
epicboon_list = None
magicitem_list = None
weapon_list = None
armor_list = None
optionalrule_list = None
item_list = None

def init(folder='data'):
    global datafolder, sources_order, class_list, race_list, background_list, spell_list, feat_list, epicboon_list, magicitem_list, weapon_list, armor_list, optionalrule_list, item_list

    datafolder = folder

    sources_order = archiver.load(os.path.join(datafolder, 'sources.json'))
    
    class_list = load('class')
    race_list = load('race')
    background_list = load('background')
    spell_list = load('spell')
    feat_list = load('feat')
    epicboon_list = load('epicboon')
    magicitem_list = load('magicitem')
    weapon_list = load('weapon')
    armor_list = load('armor')
    optionalrule_list = load('optionalrule')
    item_list = get_items()

def _get_spells(d):
    spells = d.get('spells')
    if isinstance(spells, basestring):
        d['spells'] = load('spelllist/%s.json' % spells)
        if not isinstance(d['spells'], dict):
            del d['spells']
    return d

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
            
    elif folder in ['optionalrule']:
        if not folder.endswith('/'):
            folder += '/'
        
        d = {}
        for item in os.listdir(path):
            if item.endswith('.md'):
                with open(os.path.join(path, item)) as f:
                    data = f.readlines()
                    
                if len(data) > 1:
                    data = {
                        '+': data[0].strip(),
                        'name': data[1].lstrip('#').strip(),
                        'description': ''.join(data[1:])
                    }
                    
                    if sources is None or data['+'] in sources:
                        d[data['name']] = data
                    
    elif os.path.isdir(path):
        if folder.endswith('/'):
            folder = folder[:-1]
        d = {}
        for item in os.listdir(path):
            try:
                item = archiver.load(os.path.join(path, item))
            except ValueError:
                continue
            except IOError:
                continue
            if isinstance(item, dict):
                if sources is None or item.get('+') in sources:
                    if 'name' in item:
                        if folder == 'class':
                            _get_spells(item)
                        d[item['name']] = item
        
        if folder in ['class', 'race']:
            subfolder = 'sub' + folder
            
            for key in d:
                d[key][subfolder] = {}
            
            path = os.path.join(datafolder, subfolder)
            for item in os.listdir(path):
                try:
                    item = archiver.load(os.path.join(path, item))
                except ValueError:
                    continue
                if isinstance(item, dict):
                    if sources is None or item.get('+') in sources:
                        if 'name' in item and '@' in item and item['@'] in d:
                            _get_spells(item)
                            d[item['@']][subfolder][item['name']] = item
                                
    else: #folder.find('.') > -1:
        try:
            with open(path) as f:
                d = f.read()
        except IOError:
            d = None
            
    return d

def _get_items(lst, sources, dir):
    global datafolder
    for folder in os.listdir(os.path.join(datafolder, dir)):
        path = os.path.join(datafolder, dir, folder)
        if os.path.isdir(path): # check each folder in 'items'
            data = load(os.path.join(dir, folder), sources)
            
            if data and os.path.isfile(os.path.join(path, 'description.md')):
                # if the folder is a data folder put it in items
                data['group'] = True
                
                with open(os.path.join(path, 'description.md'), 'r') as f:
                    temp = f.readlines()
                data['name'] = temp[0].strip() # get name
                
                if len(temp) > 2: # get description
                    data['description'] = ''.join(temp[2:])
                        
                _get_items(data, sources, os.path.join(dir, folder))
                
                lst[data['name']] = data

def get_items(sources=sources_order):
    dir = 'item/'
    item_list = load(dir, sources)
    if item_list is not None:
        _get_items(item_list, sources, dir)
    return item_list

def slug(s):
    r"""
    gets a "slug", a filename compatible,
    version of a string
    """
    s = s.lower()
    s = s.replace(' ', '-')
    s = s.replace("'", '')
    s = s.replace(',', '')
    s = s.replace('/', '-')
    return s

def _release_key(key, d):
    global sources_order
    
    item = d[key]
    if item == None or not isinstance(item, dict) or not item.has_key('+'):
        return str(key)
    else:
        source = item['+']
        if source in sources_order:
            index = sources_order.index(source)
        elif source == 'UA-MODERN':
            index = len(sources_order) + 1
        elif source.startswith('UA'):
            index = len(sources_order)
        else:
            index = len(sources_order) + 2
        return '%5d %s' % (index, str(key))

def release_sort(lst):
    if isinstance(lst, dict):
        return sorted(lst.keys(), key=lambda key: _release_key(key, lst))
    else:
        return sorted(lst)

# ----#-

def _has_sub(keys, in_, sub):
    out = {}
    for key in keys:
        if isinstance(keys[key], dict) and any(keys[key].values()):
            c = {}
            c.update(in_[key])
            subs = {}
            for subkey in keys[key]:
                if keys[key][subkey]:
                    subs[subkey] = in_[key][sub][subkey]
            c[sub] = subs
            out[key] = c
        elif keys[key] == True:
            out[key] = in_[key]
    return out

def _no_sub(keys, in_):
    return {key: in_[key] for key in keys if keys[key]}

def _middleman(keys, a, in_, sub=None):
    if in_ is not None:
        if keys is not None and a in keys:
            if sub is not None:
                return _has_sub(keys[a], in_, sub)
            else:
                return _no_sub(keys[a], in_)
        else:
            return in_
    else:
        return {}

# ----#-

def getclasses(keys=None):
    lst = _middleman(keys, 'class', class_list, 'subclass')
    if keys is not None:
        for class_ in lst:
            spells = lst[class_].get('spells', {})
            for lvl in spells:
                spells[lvl] = filter(lambda a: keys['spell'][a], spells[lvl])
    return lst

def getraces(keys=None):
    return _middleman(keys, 'race', race_list, 'subrace')

def getbackgrounds(keys=None):
    return _middleman(keys, 'background', background_list)

def getspells(keys=None):
    return _middleman(keys, 'spell', spell_list)

def getfeats(keys=None):
    return _middleman(keys, 'feat', feat_list)

def getepicboons(keys=None):
    return _middleman(keys, 'epicboon', epicboon_list)

def getmagicitems(keys=None):
    return _middleman(keys, 'magicitem', magicitem_list)

def getweapons(keys=None):
    return _middleman(keys, 'weapon', weapon_list)

def getarmors(keys=None):
    return _middleman(keys, 'armor', armor_list)

def getitems(keys=None):
    if item_list is not None:
        return item_list
    else:
        return {}

def getoptionalrules(keys=None):
    return _middleman(keys, 'optionalrule', optionalrule_list)

# ----#-

def class2html(c, keys=None):
    cs = getclasses(keys)
    if c in cs:
        return classes.class2html(cs[c], getspells(keys), release_sort)
    else:
        return None

def race2html(r, keys=None):
    rs = getraces(keys)
    if r in rs:
        return races.race2html(rs[r], getspells(keys), release_sort)
    else:
        return None

def background_page(keys=None):
    return backgrounds.main(getbackgrounds(keys), load)

def spell_page(keys=None):
    return spells.main(getspells(keys), getclasses(keys), load)

def magicitem_page(keys=None):
    return magicitems.main(getmagicitems(keys), getspells(keys), load)

def feat_page(keys=None):
    return feats.main(getfeats(keys), getspells(keys), load)

def boon_page(keys=None):
    return feats.boons(getepicboons(keys), getspells(keys), load)

def item_page(keys=None):
    return items.main(getweapons(keys), getarmors(keys), getitems(keys), load)

def optionalrule_page(key, keys=None):
    rules = getoptionalrules(keys)
    if key in rules:
        data = rules[key]['description']
        html = utils.convert(data)
        html = utils.get_details(html)
        html = '<div>\n%s\n</div>\n' % html
        return html
    else:
        return None

def documentation(page):
    page += '.md'
    data = load(page)
    if data is not None:
        html = utils.convert(data)
        html = utils.get_details(html)
        html = '<div>\n%s\n</div>\n' % html
        return html
    else:
        return None

# ----#-

if __name__ == '__main__':
    init('../data')
    show = load('filter/official.json')
    print '\n\n'.join(map(lambda a: '\n'.join(sorted(a)), [
        getclasses(show),
        #getraces(show),
        #getbackgrounds(show),
        #getspells(show),
        #getfeats(show),
        #getepicboons(show),
        #getmagicitems(show),
        #getweapons(show),
        #getarmors(show),
        #getitems(show),
        #getoptionalrules(show)
    ]))
    #print '\n'.join(sorted(getclasses(show)['Sorcerer']['spells']['Cantrip']))
