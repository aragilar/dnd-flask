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
            'level': str(self.level) if self.level > 0 else "0cantrip",
            'range': self.range,
            'ritual': self.ritual,
            'type': self.school,
        }
        return d

    def md(self):
        ret = '# %s\n\n' % self.name

        if self.level == 0:
            lvl = '%s Cantrip' % self.school
        else:
            lvl = '%s-level %s' % (utils.ordinals[self.level], self.school)

        if self.ritual:
            lvl += ' (ritual)'

        ret += '*%s*  \n' % lvl

        ret += '**Casting Time:** %s  \n' % self.cast_time
        ret += '**Range:** %s  \n' % self.range

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

        ret += '**Components:** %s  \n' % ', '.join(lst)
        ret += '**Duration:** %s\n\n' % self.duration

        ret += self.description

        return ret

    def page(self):
        ret = self.md()
        ret = utils.convert(ret)
        ret = handle_spells(ret, self.parent.get_spell_list(Spells))

        return ret

def handle_spells(text, spells):
    spelllist = _spellexpression_p.findall(text)
    spelllist += _spellexpression.findall(text)
    for item in spelllist:
        text = text.replace(item[0], spellblock(item[-1], spells))
    # text = re.sub(r'</div>\s*<div class="spell-list">', '', text)
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
        ret = utils.popup_group(
            utils.popup_block(name, spell.page(), body_class="spell-box"),
            body_class="spell-list"
        )
    else:
        ret = str(name)
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
                name = item["name"]
                d[name] = []
                for level in range(10):
                    level = "cantrips" if level == 0 else "level_%d_spells" % level
                    level = item[level]
                    if level:
                        level = level.split("\v")
                        d[name].extend(level)
            return d
        else:
            return {}

    def page(self):
        byClass = self.spells_by_class()
        spellscopy = {}
        for spell in self.values():
            spellscopy[spell.name] = spell.dict()

        ret = '<script>\nspells = %s;\n\nclasses = %s\n</script>\n' % (
            json.dumps(spellscopy, sort_keys=True),
            json.dumps(byClass, sort_keys=True),
        )

        ret += self.head

        ret += '''
        <div class="search-box clearfix">
        <h2>Search</h2>
        '''

        if byClass:
            ret += '<div class="pull-right">\n'
            for c in sorted(byClass.keys()):
                ret += '<p><label><input type="checkbox" class="filter" id="{0}"> {0}</label></p>\n'.format(c)
            ret += '</div>\n'

        ret += '''
        <p>Name: <input class="filter" id="name"></p>
        <br>
        <p>Level: <input class="filter" id="level"></p>
        <p>School: <input class="filter" id="type"></p>
        <p><label>Ritual: <input type="checkbox" class="filter" id="ritual"></label></p>
        <br>
        <p>Count: <span id="count">0</span></p>
        </div>
        '''

        temp = ''.join(map(
                lambda a: '<li><a href="{1}">{0}</a></li>\n'.format(a, utils.slug(a)),
                self.keys(),
        ))
        ret += '<ul id="spells" class="link-list">\n%s</ul>\n' % temp

        return ret
