import os
import re

from . import archiver
from . import utils

_spellexpression = re.compile('''(?<!<p>)(
<spell>
(.*?)
</spell>
)(?!</p>)''', re.X)

_spellexpression_p = re.compile('''(
<p>
<spell>
(.*?)
</spell>
</p>
)''', re.X)

class Spell (utils.Base):
    cast_time = 'Unknown Casting Time'
    components = {}
    description = []
    duration = 'Unknown Duration'
    level = '0'
    range = 'Unknown Range'
    ritual = False
    type = 'Unknown Type'
    
    _page = None
    
    def dict(self):
        d = {
            'name': self.name,
            'cast time': self.cast_time,
            'components': self.components,
            'duration': self.duration,
            'level': self.level,
            'range': self.range,
            'ritual': self.ritual,
            'type': self.type,
        }
        return d
    
    def __str__(self):
        if self._page is None:
            ret = '<h2>%s</h2>\n' % self.name
            
            if self.level == 'Cantrip':
                lvl = '%s Cantrip' % self.type
            else:
                lvl = '%s-level %s' % (utils.ordinals[int(self.level)], self.type)
            
            if self.ritual:
                lvl += ' (ritual)'
            
            ret += '<p>\n<em>%s</em><br>\n' % lvl
            
            ret += '<strong>Casting Time:</strong> %s<br>\n' % self.cast_time
            ret += '<strong>Range:</strong> %s<br>\n' % self.range
            
            lst = []
            truncated = True
            
            if self.components.get('verbal', False):
                lst.append('Verbal')
                if truncated:
                    lst[-1] = lst[-1][0]
            if self.components.get('somatic', False):
                lst.append('Somatic')
                if truncated:
                    lst[-1] = lst[-1][0]
            if self.components.get('material'):
                lst.append('Material')
                if truncated:
                    lst[-1] = lst[-1][0]
                lst[-1] += ' (%s)' % self.components.get('material', 'Unknown Material Component')
            
            if len(lst) == 0:
                lst.append('None')
            
            ret += '<strong>Components:</strong> %s<br>\n' % ', '.join(lst)
            ret += '<strong>Duration:</strong> %s\n</p>\n' % self.duration
            
            ret += utils.convert('\n'.join(self.description))
            ret = handle_spells(ret, self.spell_list)
            
            ret = '<div>\n%s</div>' % ret
            
            self._page = ret
        else:
            ret = self._page
        
        return ret

def spells_by_class(classes):
    new = {}
    for c in classes.values():
        d = []
        
        slist = c.spells
        
        for x in slist.keys():
            d.extend(slist.get(x, []))
        d.sort()
        if len(d):
            new[c.name] = d
    return new

def handle_spells(text, spells):
    spelllist = _spellexpression_p.findall(text)
    spelllist += _spellexpression.findall(text)
    for item in spelllist:
        text = text.replace(item[0], utils.details_group(spellblock(item[-1], spells)))
    return text

def spellblock(name, spells=None):
    if name is None:
        name = ''
        spell = None
    elif spells is None:
        spell = name
        name = spell.name
    else:
        spell = spells.get(name)
    if spell is not None:
        ret = utils.details_block(
            str(name),
            str(spell),
            body_class="spell-box"
        )
    else:
        ret = str(name)
    return ret

class Spells (utils.Group):
    type = Spell
    
    javascript = ['spells.js']
    head = '<h1>Spells</h1>\n'
    classes = {}
    
    def __init__(self, folder=None, sources=None):
        super().__init__(folder, sources)
        if folder:
            folder = os.path.join(folder, 'documentation/spellcasting.md')
            if os.path.exists(folder):
                with open(folder, 'r') as f:
                    data = f.read()
                data = utils.convert(data)
                data = utils.get_details(data)
                data = utils.get_details(data, 'h1')
                self.head = data
    
    def set_class_list(self, value):
        self.classes = value
    
    def filter(self, f=None):
        r = super().filter(f)
        if hasattr(r.classes, 'filter'):
            r.classes = r.classes.filter(f)
        return r

    def page(self):
        ret = '<div>\n'
        byClass = spells_by_class(self.classes)
        spellscopy = {}
        for spell in self.values():
            spellscopy[spell.name] = spell.dict()
        
        ret += '<script>\nspells = %s;\n\nclasses = %s\n</script>\n' % (
            archiver.p(spellscopy, compact=True),
            archiver.p(byClass, compact=True)
        )
        
        ret += self.head
        
        ret += '''
        <div class="search-box">
        <h2>Search</h2>
        <p>Name: <input class="filter" id="name"></p>
        <p>
            Level: <input class="filter" id="level">
            <br>
            School: <input class="filter" id="type">
            <br>
            <label>Ritual: <input type="checkbox" class="filter" id="ritual"></label>
        </p>
        '''
        
        if byClass:
            ret += '<p class="right">\n'
            for c in sorted(byClass.keys()):
                ret += '<label><input type="checkbox" class="filter" id="{0}"> {0}</label>\n<br>\n'.format(c)
            ret += '</p>\n'
        
        ret += '''
        <p>Count: <output id="count">0</output></p>
        </div>
        '''

        temp = ''.join(utils.asyncmap(
                spellblock,
                self.values(),
        ))
        ret += utils.details_group(temp, body_id="spells", body_class="spell-table")
        ret += '</div>\n'

        return ret
