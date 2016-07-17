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
    spelllist = list(_spellexpression_p.finditer(text))
    spelllist += list(_spellexpression.finditer(text))
    spelllist = map(lambda a: a.groups(), spelllist)
    for item in spelllist:
        text = text.replace(item[0], utils.details_group(spellblock(item[-1], spells)))
    return text

def spellblock(name, spells=None):
    if name is None:
        name = ''
        item = None
    elif spells is None:
        spell = name
        name = spell.name
    else:
        spell = spells.get(name)
    if spell is not None:
        ret = utils.details_block(
            str(name),
            '<div>\n%s</div>' % str(spell),
            body_class="spell-box"
        )
    else:
        ret = str(name)
    return ret

class Spells (utils.Group):
    type = Spell

    def page(self, classes, load):
        ret = '<div>\n'
        byClass = spells_by_class(classes)
        spellscopy = {}
        for spell in self.values():
            spellscopy[spell.name] = spell.dict()
        
        ret += '<script>\nspells = %s;\n\nclasses = %s\n</script>\n' % (
            archiver.p(spellscopy, compact=True),
            archiver.p(byClass, compact=True)
        )
        
        temp = load('spellcasting.md')
        if temp:
            ret += utils.get_details(utils.get_details(utils.convert(temp)), 'h1')
        else:
            ret += '<h1>Spells</h1>\n'
        ret += '<div style="padding: 5px; margin: 5px auto;">\n'
        
        for c in sorted(byClass.keys()):
            ret += '\t<label style="clear: right; float: right; padding: 2px;">%s: <input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="%s"></label>\n' % (c, c)
        
        ret += '''
        <h2>Search</h2>
        Name: <input style="padding: inherit; margin: inherit;" class="filter" id="name"><br>
        Level: <input style="padding: inherit; margin: inherit;" class="filter" id="level"><br>
        School: <input style="padding: inherit; margin: inherit;" class="filter" id="type"><br>
        <label>Ritual: <input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="ritual"></label><br>
        
        <!--Nonverbal: <input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="nonverbal"><br>
        Nonsomatic: <input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="nonsomatic"><br>
        Immaterial: <input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="immaterial"><br>-->
        <span style="margin: 5px; display: block; clear: both;">Count: <output id="count">0</output></span>
        </div>
        '''

        temp = ''.join(utils.asyncmap(
                spellblock,
                self.values(),
        ))
        ret += utils.details_group(temp, body_id="spells", body_class="spell-table")
        ret += '</div>\n'

        return ret
