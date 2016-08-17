import os
import re
import collections
import copy
import multiprocessing.pool

import markdown2

from . import archiver

md = markdown2.Markdown(
    html4tags=True,
    extras = [
        'fenced-code-blocks',
        'markdown-in-html',
        'tables',
    ],
)

_lock = multiprocessing.Lock()
def convert(data):
    _lock.acquire()
    out = md.convert(data)
    _lock.release()
    return out

class Base (object):
    _translate = {
        '+': 'source',
        '@': 'parent',
        'A': 'index',
    }
    
    name = ''
    spell_list = {}
    source = ''
    index = float('inf')
    parent = None
    children = collections.OrderedDict()
    subclass = None
    
    def __init__(self, d={}):
        for key, value in d.items():
            if key in self._translate:
                key = self._translate[key]
            key = key.replace(' ', '_')
            setattr(self, key, value)
        if self.subclass:
            self.children = collections.OrderedDict()
    
    @classmethod
    def fromJSON(cls, d):
        if isinstance(d, dict):
            if 'name' in d:
                d = cls(d)
        return d
    
    def filter(self, filter=None):
        ret = copy.copy(self)
        if filter is not None and type(self).__name__.lower() in filter:
            filter = filter[type(self).__name__.lower()]
            if self.name not in filter:
                ret = None
            else:
                f = filter[self.name]
                if not f:
                    ret = None
                elif self.subclass:
                    ret.children = collections.OrderedDict()
                    for child in self.children.values():
                        child = child.subfilter(f)
                        if child:
                            ret.children[child.name] = child
                    if not ret.children and not f == True:
                        ret = None
        return ret
    
    def subfilter(self, filter=None):
        ret = copy.copy(self)
        if filter is not None:
            if self.name not in filter or not filter[self.name]:
                ret = None
        return ret
    
    def set_spell_list(self, spell_list):
        self.spell_list = spell_list
        if self.children:
            for child in self.children.values():
                child.set_spell_list(spell_list)
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        s = '{}({})'.format(
            type(self).__name__,
            self.name,
        )
        if self.subclass:
            s += ': '
            s += ', '.join(map(repr, self.children.values()))
        return s

class Group (object):
    type = Base
    spell_list = {}

    def __loadfile(self, filename, folder, sources=None):
        item = os.path.join(folder, filename)
        if os.path.isfile(item) and item.endswith('.json'):
            try:
                item = self.type(archiver.load(item))
            except (ValueError, IOError):
                raise
            if sources is None or item.source in sources:
                self.add(item)
    
    def __init__(self, folder=None, sources=None):
        self._items = collections.OrderedDict()
        if folder:
            folder = os.path.join(folder, self.type.__name__.lower())
            if os.path.exists(folder):
                asyncmap(
                    lambda a: self.__loadfile(a, folder, sources),
                    os.listdir(folder),
                )
                
                # ----#-         Sub
                if self.type.subclass:
                    if folder.endswith('/') or folder.endswith('\\'):
                        folder = folder[:-1]
    
                    folder = os.path.split(folder)
                    folder = os.path.join(folder[0], self.type.subclass.__name__.lower())
    
                    l = []
                    for item in os.listdir(folder):
                        item = os.path.join(folder, item)
                        if os.path.isfile(item) and item.endswith('.json'):
                            try:
                                item = self.type.subclass(archiver.load(item))
                            except (ValueError, IOError):
                                raise
                            if sources is None or item.source in sources:
                                l.append(item)
    
                    for item in l:
                        if item.parent in self:
                            self[item.parent].children[item.name] = item
            self.sort()
            if self.type.subclass:
                if sources:
                    self.sort(key=lambda a: sources.index(a.source))
                self.sort(key=lambda a: a.index)
    
    def add(self, item):
        if isinstance(item, self.type):
            self._items[item.name] = item
        else:
            raise TypeError('Cannot accept item of type %s' % str(type(item)))
    
    def filter(self, f):
        new = copy.copy(self)
        new._items = collections.OrderedDict()
        for item in self.values():
            item = item.filter(f)
            if item is not None:
                new.add(item)
        return new
    
    def set_spell_list(self, spell_list):
        self.spell_list = spell_list
        for item in self:
            item.set_spell_list(spell_list)
    
    def keys(self):
        return self._items.keys()
    
    def values(self):
        return self._items.values()
    
    def items(self):
        return self._items.items()
    
    def get(self, item, default=None):
        if item in self:
            default = self[item]
        return default
    
    def sort(self, key=lambda a: a.name):
        for item in sorted(self._items.values(), key=key):
            self._items.move_to_end(item.name)
            if isinstance(item, self.type) and item.children:
                for sub in sorted(item.children.values(), key=key):
                    item.children.move_to_end(sub.name)
            elif isinstance(item, type(self)):
                item.sort(key)
    
    def keymap(self):
        return {slug(k): k for k in self._items.keys()}
    
    def __iter__(self):
        return iter(self._items.values())
    
    def __len__(self):
        return len(self._items)
    
    def __contains__(self, key):
        return key in self._items or key in self.keymap()
    
    def __getitem__(self, key):
        km = self.keymap()
        if key in self._items:
            return self._items[key]
        elif key in km:
            return self._items[km[key]]
        else:
            return self._items[key]

    def __str__(self):
        return str(list(self.values()))

    def __nonzero__(self):
        return len(self) > 0

def slug(s):
    r"""
    gets a "slug", a filename compatible
    version of a string
    """
    s = s.lower()
    for item in ' /':
        s = s.replace(item, '-')
    for item in "',:":
        s = s.replace(item, '')
    return s

def comma_list(lst, joiner = 'and'):
    if len(lst) > 2 or joiner == None:
        ret = ', '.join(lst[:-1])
        ret += ', '
        if joiner != None:
            ret += '%s ' % joiner
        ret += str(lst[-1])
    elif len(lst) > 0:
        ret = (' %s ' % joiner).join(lst)
    else:
        ret = 'none'
    return ret

def choice_list(lst, type = ''):
    if type != '':
        type = ' ' + type
    if lst:
        choose = None
        for x, item in enumerate(lst):
            if isinstance(item, int):
                choose = x
                break
        
        if (type and choose is not None
                and lst[choose] > 1):
            type += 's'
        
        if choose is not None and len(lst) > 1:
            choices = comma_list(lst[choose+1:], 'or')
            if choose == 0:
                ret = 'Choose %d%s from %s' % (
                    lst[choose],
                    type,
                    choices
                )
            else:
                ret = '%s, and %d%s from %s' % (
                    comma_list(lst[:choose]),
                    lst[choose],
                    type,
                    choices
                )
        elif choose is not None:
            if lst[choose] > 1:
                ret = 'Choose any %d%s' % (lst[choose], type)
            else:
                ret = 'Choose any%s' % type
        else:
            ret = comma_list(lst)
    else:
        ret = 'none'
    return ret

def get_details(text, detltag='h2', splttag=None):
    if splttag is not None:
        blocks = text.split('<{}'.format(splttag))
    else:
        blocks = [text]
    
    for x, text in enumerate(blocks):
        repl = re.findall('(<{0}.*?>.*?</{0}>)(.+?)(?=<{0}|$)'.format(detltag), text, re.DOTALL)
        if repl:
            head = text[:text.find(repl[0][0])]
            new = ''
            for item in repl:
                new += details_block(item[0], item[1])
            blocks[x] = head + details_group(new)
    
    if splttag is not None:
        text = '<{}'.format(splttag).join(blocks)
    else:
        text = ''.join(blocks)
    return text

def details_block(summary, body=None, summary_class=None, body_class=None):
    if body:
        if summary_class:
            txt = '<dt class="%s">' % summary_class
        else:
            txt = '<dt>'
        txt += summary
        txt += '</dt>\n'
    
        if body_class:
            txt += '<dd class="%s">' % body_class
        else:
            txt += '<dd>'
        if not body.startswith('\n'):
            txt += '\n'
        txt += body
        if not body.endswith('\n'):
            txt += '\n'
        txt += '</dd>\n'
    else:
        txt = summary
    return txt

def details_group(text, body_id=None, body_class=None):
    c = 'accordion'
    if body_class:
        c += ' ' + body_class

    d = ''
    if body_id:
        d = ' id="%s"' % body_id
    
    return '<dl%s class="%s">\n%s</dl>\n' % (d, c, text)

def asyncmap(func, lst):
    with multiprocessing.pool.ThreadPool() as pool:
        new = pool.map(func, lst)
    return new

def get_modifier(num):
    num = int(num)
    num -= 10
    num //= 2
    return num

stats = collections.OrderedDict([
    ('str', 'Strength'),
    ('dex', 'Dexterity'),
    ('con', 'Constitution'),
    ('int', 'Intelligence'),
    ('wis', 'Wisdom'),
    ('cha', 'Charisma'),
])
statlist = stats.keys()

ordinals = [
    '0th',
    '1st',
    '2nd',
    '3rd',
    '4th',
    '5th',
    '6th',
    '7th',
    '8th',
    '9th',
    '10th',
    '11th',
    '12th',
    '13th',
    '14th',
    '15th',
    '16th',
    '17th',
    '18th',
    '19th',
    '20th',
]

experience = [
    0,
    300,
    900,
    2700,
    6500,
    14000,
    23000,
    34000,
    48000,
    64000,
    85000,
    100000,
    120000,
    140000,
    165000,
    195000,
    225000,
    265000,
    305000,
    355000,
]

spellslots = [
    [0,0,0,0,0,0,0,0,0],
    [2,0,0,0,0,0,0,0,0],
    [3,0,0,0,0,0,0,0,0],
    [4,2,0,0,0,0,0,0,0],
    [4,3,0,0,0,0,0,0,0],
    [4,3,2,0,0,0,0,0,0],
    [4,3,3,0,0,0,0,0,0],
    [4,3,3,1,0,0,0,0,0],
    [4,3,3,2,0,0,0,0,0],
    [4,3,3,3,1,0,0,0,0],
    [4,3,3,3,2,0,0,0,0],
    [4,3,3,3,2,1,0,0,0],
    [4,3,3,3,2,1,0,0,0],
    [4,3,3,3,2,1,1,0,0],
    [4,3,3,3,2,1,1,0,0],
    [4,3,3,3,2,1,1,1,0],
    [4,3,3,3,2,1,1,1,0],
    [4,3,3,3,2,1,1,1,1],
    [4,3,3,3,3,1,1,1,1],
    [4,3,3,3,3,2,1,1,1],
    [4,3,3,3,3,2,2,1,1],
]
