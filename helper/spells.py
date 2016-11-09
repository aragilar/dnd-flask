import os
import re
import json

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
    def __init__(self, parent, d):
        for key, value in {
            "level": -1,
            "school": "Unknown School",
            "cast_time": "Unknown casting time",
            "range": "Unknown range",
            "duration": "Unknown duration",
        }.items():
            if d[key] is None:
                d[key] = value

        super().__init__(parent, d)

    def dict(self):
        d = {
            'name': self.name,
            'cast time': self.cast_time,
            'duration': self.duration,
            'level': self.level,
            'range': self.range,
            'ritual': self.ritual,
            'type': self.school,
        }
        return d

    def page(self):
        ret = '<h2>%s</h2>\n' % self.name

        if self.level == 0:
            lvl = '%s Cantrip' % self.school
        else:
            lvl = '%s-level %s' % (utils.ordinals[self.level], self.school)

        if self.ritual:
            lvl += ' (ritual)'

        ret += '<p>\n<em>%s</em><br>\n' % lvl

        ret += '<strong>Casting Time:</strong> %s<br>\n' % self.cast_time
        ret += '<strong>Range:</strong> %s<br>\n' % self.range

        lst = []
        truncated = True

        if self.verbal:
            lst.append('Verbal')
            if truncated:
                lst[-1] = lst[-1][0]
        if self.somatic:
            lst.append('Somatic')
            if truncated:
                lst[-1] = lst[-1][0]
        if self.material:
            lst.append('Material')
            if truncated:
                lst[-1] = lst[-1][0]
            lst[-1] += ' (%s)' % self.material

        if len(lst) == 0:
            lst.append('None')

        ret += '<strong>Components:</strong> %s<br>\n' % ', '.join(lst)
        ret += '<strong>Duration:</strong> %s\n</p>\n' % self.duration

        ret += utils.convert(self.description)
        ret = handle_spells(ret, self.parent.get_spell_list(Spells))

        ret = '<div>\n%s</div>' % ret

        return ret

def handle_spells(text, spells):
    spelllist = _spellexpression_p.findall(text)
    spelllist += _spellexpression.findall(text)
    for item in spelllist:
        text = text.replace(item[0], utils.details_group(spellblock(item[-1], spells)))
    text = re.sub(r'</dl>\s*<dl class="accordion">', '', text)
    #text = text.replace('</dl>\n\n\n<dl class="accordion">', '\n')
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
            spell.page(),
            body_class="spell-box"
        )
    else:
        ret = '<p>%s</p>\n' % str(name)
    return ret

class Spells (utils.Group):
    type = Spell
    tablename = "spells"
    javascript = ['spells.js']
    
    @property
    def head(self):
        return self.get_document("Spellcasting", "Spells")

    def spells_by_class(self):
        if self.db:
            with self.db as db:
                l = db.select("spell_lists")
            d = {}
            for item in l:
                d[item["name"]] = []
                for level in range(10):
                    level = "cantrips" if level == 0 else "level_%d_spells" % level
                    d[item["name"]].extend(item[level].split("\v"))
            return d
        else:
            return {}

    def page(self):
        ret = '<div>\n'
        byClass = self.spells_by_class()
        spellscopy = {}
        for spell in self.values():
            spellscopy[spell.name] = spell.dict()

        ret += '<script>\nspells = %s;\n\nclasses = %s\n</script>\n' % (
            json.dumps(spellscopy, sort_keys=True),
            json.dumps(byClass, sort_keys=True),
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
