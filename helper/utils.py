import os
import re
import collections
import functools
import copy
import multiprocessing.pool
import json
import uuid

##import markdown
import markdown2

md = markdown2.Markdown(
    html4tags=True,
    extras = [
        'definition-lists',
        'fenced-code-blocks',
        'markdown-in-html',
        'smarty-pants',
        'tables',
    ],
)

##md = markdown.Markdown(
##    extensions = [
##        "markdown.extensions.def_list",
##        "markdown.extensions.fenced_code",
##        "markdown.extensions.tables",
##        "markdown.extensions.smarty",
##    ]
##)

_lock = multiprocessing.Lock()
def convert(data):
    _lock.acquire()
    out = md.convert(data)
    _lock.release()
    return out

class Base (object):
    children = None

    def __init__(self, parent, d, children=None):
        self.parent = parent

        d = unjson(d)

        for key, value in d.items():
            setattr(self, key, value)

    def __str__(self):
        return self.name

    def __repr__(self):
        s = '{}({})'.format(
            type(self).__name__,
            self.name,
        )
        if self.children:
            s += ': '
            s += ', '.join(map(repr, self.children.values()))
        return s

    def page(self):
        return '<div class="alert alert-danger" role="alert">This object has no <code>page</code> method.</div>'

class Group (object):
    type = Base
    subtype = None
    tablename = None

    def __init__(self, db=None, f=None):
        self.db = db
        self.current_filter = f

    def __call__(self, db):
        self.db = db

    def filter(self, f=None):
        if f:
            c = copy.copy(self)
            c.current_filter = f
            return c
        else:
            return self

    def get_data(self, columns=["*"], name=None, subtype_item=None):
        if self.db:
            tables = ['%s C' % self.tablename, 'Sources S']
            conditions = ["C.source==S.id"]
            params = []
            if name is not None:
                conditions.append("slug(C.name)=?")
                params.append(slug(name))
            order = [
                "case when C.sort_index is null then 1 else 0 end",
                "C.sort_index",
                "C.name",
            ]
            if self.subtype:
                order.insert(2, "S.source_index")

            if self.current_filter:
                tables.append('%s_filters F' % self.tablename)
                conditions.append('C.name == F.item_name')
                conditions.append("F.filter_name == '%s'" % self.current_filter.replace("'", "''"))

            if subtype_item:
                tables[0] = 'sub' + tables[0]
                if self.current_filter:
                    tables[-1] = 'sub' + tables[-1]
                conditions.append("C.%s=='%s'" % (
                    self.type.__name__.lower(),
                    subtype_item.replace("'", "''"),
                ))

            with self.db as db:
                if name is not None:
                    self.db.conn.create_function("slug", 1, slug)
                data = db.select(
                    tables,
                    columns=list(map("C.".__add__, columns)),
                    conditions=conditions,
                    order=order,
                    params=params,
                )
##                data = map(dict, data)
##                data = list(data)
                return data
        else:
            return []

    def get_document(self, doc, default=None):
        with self.db as db:
            text = db.select('documents', conditions="name=='%s'" % doc)
        if text:
            text = text[0]
            title = "<h1>%s</h1>\n\n" % text['name']
            body = convert(text['description'])
            body = get_details(body)
            text = details_block(title, body)
            text = details_group(text)
        else:
            if default:
                text = '<h1>%s</h1>\n' % default
            else:
                text = None
        return text

    def add_children(self, parent):
        if self.subtype:
            parent.children = collections.OrderedDict()
            data = self.get_data(subtype_item=parent.name)
            for sub in data:
                sub = self.subtype(self, sub)
                parent.children[sub.name] = sub
        return parent

    def keys(self):
        return (item["name"] for item in self.get_data(columns=["name"]))

    def values(self):
        values = self.get_data()
        values = map(functools.partial(self.type, self), values)
        values = list(values)
        for item in values:
            self.add_children(item)
        return values

    def dict(self):
        items = list(self.values())
        names = (item.name for item in items)
        return collections.OrderedDict(zip(names, items))

    def items(self):
        return self.dict().items()

    def get(self, key, default=None):
        if key in self:
            default = self[key]
        return default

    __iter__ = keys

    def __len__(self):
        return len(self.get_data())

    def __contains__(self, key):
        return slug(key) in map(slug, self.keys())

    def __getitem__(self, key):
##        keys = {slug(key): key for key in self.keys()}
##        key = keys[slug(key)]
        data = self.get_data(name=key)
        data = dict(data[0])
        data = self.type(self, data)
        self.add_children(data)
        return data

    def __str__(self):
        return str(list(self.values()))

    def __nonzero__(self):
        return len(self) > 0

    def get_spell_list(self, SpellsClass):
        return SpellsClass(self.db)

def unjson(d):
    new = {}
    for key, value in d.items():
        if isinstance(value, str):
            if isinstance(value, str) and value.endswith("\v"):
                item = value.split("\v")
                item.pop()
                value = item
            elif (value.startswith("{") and value.endswith("}")
                    or value.startswith("[[") and value.endswith("]]")):
                value = json.loads(value)
        new[key] = value
    return new

def tojson(d):
    new = {}
    for key, value in d.items():
        if isinstance(value, dict):
            value = json.dumps(value, sort_keys=True)
        elif isinstance(value, list):
            try:
                item = "\v".join(value) + "\v"
            except TypeError:
                item = json.dumps(value, sort_keys=True)
            value = item
        new[key] = value
    return new

def slug(s):
    r"""
    gets a "slug", a filename compatible
    version of a string
    """
    #s = bytearray(s, 'utf_8').decode('ascii', errors='ignore')
    s = s.strip()
    s = s.lower()
    s = s.replace("&#8217;", "'")
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

def choice_list(lst, type=''):
    lst = [int(item) if isinstance(item, int) or item.isdigit() else item for item in lst]
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
        id = uuid.uuid4()
        sclass = "collapse-toggle"
        if summary_class:
            sclass += ' ' + summary_class
        txt = '<button class="{1}" data-toggle="collapse" data-target="#{0}" aria-expanded="false" aria-controls="{0}">'.format(id, sclass)
        txt += summary
        txt += '</button>\n'

        bclass = "collapse"
        if body_class:
            bclass += ' ' + body_class
        txt += '<div id="{0}" class="{1}" aria-expanded="false">'.format(id, bclass)
        if not body.startswith('\n'):
            txt += '\n'
        txt += body
        if not body.endswith('\n'):
            txt += '\n'
        txt += '</div>\n'
    else:
        txt = summary
    return txt

def details_group(text, body_id=None, body_class=None):
    c = ''
    if body_class:
        c = ' class="%s"' % body_class

    d = ''
    if body_id:
        d = ' id="%s"' % body_id

    return '<div%s%s>\n%s</div>\n' % (d, c, text)

def popup_block(summary, body=None, summary_class=None, body_class=None):
    if body:
        sclass = "btn btn-default btn-sm dropdown-toggle"
        if summary_class:
            sclass += ' ' + summary_class
        txt = '<button type="button" class="{0}" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">'.format(sclass)
        txt += summary
        txt += ' <span class="caret"></span>'
        txt += '</button>\n'

        bclass = "dropdown-menu"
        if body_class:
            bclass += ' ' + body_class
        txt += '<div class="{0}">'.format(bclass)
        if not body.startswith('\n'):
            txt += '\n'
        txt += body
        if not body.endswith('\n'):
            txt += '\n'
        txt += '</div>\n'
    else:
        txt = summary
    return txt

def popup_group(text, body_id=None, body_class=None):
    c = ' class="dropdown'
    if body_class:
        c += ' %s' % body_class
    c += '"'

    d = ''
    if body_id:
        d = ' id="%s"' % body_id

    return '<div%s%s>\n%s</div>\n' % (d, c, text)

def asyncmap(func, lst):
    with multiprocessing.pool.ThreadPool() as pool:
        new = pool.map(func, lst)
    return new

def get_modifier(num):
    num = int(num)
    num -= 10
    num //= 2
    return num

def remove_null(d):
    d = d.copy()
    for key in d:
        if d[key] is None:
            del d[key]
    return d

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
