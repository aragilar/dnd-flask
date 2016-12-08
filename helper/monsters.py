import os
import collections
import json

from . import utils
from . import spells

challenge_ratings = {
    0: 0,
    10: 0,
    25: 0.125,
    50: 0.25,
    100: 0.5,
    200: 1,
    450: 2,
    700: 3,
    1100: 4,
    1800: 5,
    2300: 6,
    2900: 7,
    3900: 8,
    5000: 9,
    5900: 10,
    7200: 11,
    8400: 12,
    10000: 13,
    11500: 14,
    13000: 15,
    15000: 16,
    18000: 17,
    20000: 18,
    22000: 19,
    25000: 20,
    33000: 21,
    41000: 22,
    50000: 23,
    62000: 24,
    75000: 25,
    90000: 26,
    105000: 27,
    120000: 28,
    135000: 29,
    155000: 30,
}

class Monster (utils.Base):
    def __init__(self, parent, d):
        for key, value in {
            "alignment": "unaligned",
            "challenge_description": "{cr} ({xp} XP)",
            "experience": 0,
        }.items():
            if d[key] is None:
                d[key] = value

        if d["legendary_actions"] is not None:
            d["legendary_actions"] = json.loads(d["legendary_actions"])

        super().__init__(parent, d)

    def dict(self):
        d = {
            'name': self.name,
            'alignment': self.alignment.lower(),
            'challenge rating': self._get_cr(),
            'legendary': bool(self.legendary_actions),
            'size': self.size.lower(),
            'type': self.get_type().lower(),
        }
        return d

    def _get_cr(self):
        if self.challenge_rating is None:
            c = challenge_ratings.get(self.experience, -1)
        else:
            c = self.challenge_rating
        c = float(c)
        self.challenge_rating = c
        return c

    def get_cr(self):
        c = self._get_cr()
        if c < 0:
            c = '?'
        elif c > 0 and c < 1:
            c = '1/%d' % int(1 / c)
        else:
            c = '{:g}'.format(c)
        return c

    def get_type(self):
        type = self.type
        if self.tags:
            type += ' ('
            type += ', '.join(self.tags)
            type += ')'
        return type

    def about(self):
        temp = None
        if self.description or self.monster_group:
            temp = self.description
            if self.monster_group:
                if not temp:
                    temp = '# {}'.format(self.monster_group)
                temp += '\n\n---\n\nThis monster is a member of the {0} [group](/monsters/groups/).'.format(self.monster_group)
        return temp

    def body(self):
        md = '# {}\n\n'.format(self.name)
        md += '*{size} {type}, {alignment}*\n\n'.format(
            alignment=self.alignment,
            size=self.size,
            type=self.get_type(),
        )
        md += '---\n\n'
        md += '**Armor Class** {}\n\n'.format(self.ac)
        md += '**Hit Points** {}\n\n'.format(self.hp)
        md += '**Speed** {}\n\n'.format(', '.join(self.speed))
        md += '---\n\n'

        for stat in utils.stats:
            value = self.ability_scores.get(stat, 10)
            md += '* **{}** {} ({:+})\n'.format(stat[:3].upper(), value, utils.get_modifier(value))

        md += '\n---\n\n'

        if self.saving_throws:
            title_stats = list(map(str.title, utils.stats))
            for key in self.saving_throws:
                if key not in title_stats:
                    raise ValueError("Invalid saving throw: %s" % key)
            md += '**Saving Throws** {}\n\n'.format(', '.join(
                '{} {:+}'.format(stat, self.saving_throws[stat])
                for stat in title_stats
                if stat in self.saving_throws
            ))

        if self.skills:
            skills = []
            for skill in sorted(self.skills):
                value = self.skills[skill]
                if isinstance(value, (int, float)):
                    _format = '{} {:+}'
                else:
                    _format = '{} {}'
                skills.append(_format.format(skill, value))
            md += '**Skills** {}\n\n'.format(', '.join(skills))

        for name, temp in [
            ('Damage Vulnerabilities', self.damage_vulnerabilities),
            ('Damage Resistances', self.damage_resistances),
            ('Damage Immunities', self.damage_immunities),
        ]:
            if temp:
                temp = temp.copy()
                new = []
                while temp:
                    s = []
                    while temp:
                        if ',' in temp[0]:
                            if not s:
                                s.append(temp.pop(0))
                            break
                        else:
                            s.append(temp.pop(0))
                    new.append(', '.join(s))
                md += '**{}** {}\n\n'.format(name, '; '.join(new))

        if self.condition_immunities:
            md += '**Condition Immunities** {}\n\n'.format(
                ', '.join(self.condition_immunities)
            )

        if self.senses:
            temp = self.senses.copy()
        else:
            temp = []
        if not any(item.startswith('passive Perception ') for item in temp):
            if self.skills and 'Perception' in self.skills:
                s = self.skills['Perception']
            else:
                s = utils.get_modifier(self.ability_scores.get("wis", 10))
            temp.append('passive Perception {}'.format(10 + s))
        md += '**Senses** {}\n\n'.format(', '.join(temp))

        if self.languages:
            temp = ', '.join(self.languages)
        else:
            temp = '-'
        md += '**Languages** {}\n\n'.format(temp)

        temp = self.challenge_description.replace('{xp}', '{xp:,}')
        temp = '**Challenge** {}\n\n'.format(temp)
        temp = temp.format(cr=self.get_cr(), xp=self.experience)
        md += temp

        md += '---\n\n'

        for name, temp in [
            (None, self.traits),
            ('Actions', self.actions),
            ('Reactions', self.reactions),
        ]:
            if temp:
                if name:
                    md += '## {}\n\n'.format(name)
                for item in temp:
                    if isinstance(item, list):
                        md += '***{}.*** {}\n\n'.format(item[0], '\n'.join(item[1:]).lstrip())
                    else:
                        md += item + '\n\n'

        for name, temp in [
            ('Legendary Actions', self.legendary_actions),
        ]:
            if temp:
                if name:
                    md += '## {}\n\n'.format(name)
                md += '<dl markdown="1">\n'
                for item in temp:
                    if isinstance(item, list):
                        md += '<dt>{}</dt>\n<dd>{}</dd>\n'.format(item[0], '\n'.join(item[1:]).lstrip())
                    else:
                        md += item + '\n\n'
                md += '</dl>\n'

        return md

    def md(self):
        ret = self.about()
        if ret:
            ret += '\n\n---\n---\n\n'
            if not ret.startswith("#"):
                ret = "# %s\n\n%s" % (self.name, ret)
        ret += self.body()
        ret = ret.replace('<dl markdown="1">\n', '')
        ret = ret.replace('\n</dl>', '')
        ret = ret.replace('<dt>', '**')
        ret = ret.replace('</dt>\n', '.** ')
        ret = ret.replace('<dd>', '')
        ret = ret.replace('</dd>', '')
        return ret

    def page(self):
        temp = self.about()
        if temp:
            temp = utils.convert(temp)
            if not temp.startswith('<h1'):
                temp = '<h1>{}</h1>\n'.format(self.name) + temp
            temp = utils.get_details(temp, 'h1')

        md = self.body()
        md = utils.convert(md)
        md = md.replace('<ul>', '<ul class="monster-stats">', 1)

        ret = temp
        ret += '<div class="monster-box">\n'
        ret += md
        ret += '</div>\n'

        ret = spells.handle_spells(ret, self.parent.get_spell_list(spells.Spells))

        return ret

def monsterblock(name, monsters=None):
    if name is None:
        name = ''
        monster = None
    elif monsters is None:
        monster = name
        name = monster.name
    else:
        monster = monsters.get(name)
    if monster is not None:
        ret = '<li><a href="{1}">{0}</a></li>\n'.format(name, utils.slug(name))
    else:
        ret = str(name)
    return ret

class Monsters (utils.Group):
    type = Monster
    singular = "Monster"
    plural = "Monsters"
    tables = [
    {
        "table": "monster_groups",
        "fields": utils.collections.OrderedDict([
            ("name", str),
            ("description", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "description": "NOT NULL",
        }
    },
    {
        "table": plural,
        "fields": utils.collections.OrderedDict([
            ("name", str),
            ("source", str),
            ("sort_index", int),
            ("monster_group", str),
            ("description", str),
            ("alignment", str),
            ("size", str),
            ("type", str),
            ("tags", str),
            ("ac", str),
            ("hp", str),
            ("speed", str),
            ("ability_scores", str),
            ("saving_throws", str),
            ("skills", str),
            ("damage_vulnerabilities", str),
            ("damage_resistances", str),
            ("damage_immunities", str),
            ("condition_immunities", str),
            ("senses", str),
            ("languages", str),
            ("experience", int),
            ("challenge_rating", int),
            ("challenge_description", str),
            ("traits", str),
            ("actions", str),
            ("reactions", str),
            ("legendary_actions", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
            "monster_group": "REFERENCES monster_group(name)",
            "alignment": "NOT NULL",
            "size": "NOT NULL",
            "type": "NOT NULL",
            "ac": "NOT NULL",
            "hp": "NOT NULL",
            "speed": "NOT NULL",
            "ability_scores": "NOT NULL",
            "experience": "NOT NULL",
        }
    }
    ]
    javascript = ['monsters.js']

    @property
    def head(self):
        return self.get_document("Monsters", "Monsters")

    def page(self):
        itemscopy = {}
        for item in self.values():
            itemscopy[item.name] = item.dict()

        ret = '<script>\nmonsters = %s;\n</script>\n' % (json.dumps(itemscopy, sort_keys=True))

        ret += self.head

        ret += '''
        <div class="search-box clearfix">
        <h2>Search</h2>
        <div class="pull-right">
            <p><label><input type="checkbox" class="filter size" id="tiny"> Tiny </label></p>
            <p><label><input type="checkbox" class="filter size" id="small"> Small</label></p>
            <p><label><input type="checkbox" class="filter size" id="medium"> Medium</label></p>
            <p><label><input type="checkbox" class="filter size" id="large"> Large</label></p>
            <p><label><input type="checkbox" class="filter size" id="huge"> Huge</label></p>
            <p><label><input type="checkbox" class="filter size" id="gargantuan"> Gargantuan</label></p>
        </div>
        <p>Name: <input class="filter" id="name"></p>
        <p>Type: <input class="filter" id="type"></p>
        <br>
        <p>Min CR <input class="filter" id="crge"></p>
        <p>Max CR <input class="filter" id="crle"></p>
        <br>
        <p><label><input type="checkbox" class="filter" id="legendary"> Legendary</label></p>
        <br>
        <p>Count: <span id="count">0</span></p>
        </div>
        '''

        temp = ''.join(utils.asyncmap(
            monsterblock,
            self.values(),
        ))
        ret += '<ul id="monsters" class="link-list">\n%s</ul>\n' % temp

        return ret

    @property
    def groups(self):
        with self.db as db:
            grouplist = db.select("monster_groups", order=["name"])
        grouplist = [(item["name"], item["description"]) for item in grouplist]
        grouplist = collections.OrderedDict(grouplist)
        return grouplist

    def groups_page(self):
        groups = self.groups

        ret = ''
        monster_list = self.values()
        for group in groups:
            lst = []
            for item in monster_list:
                if item.monster_group == group:
                    lst.append(item)
            if lst:
                temp = groups[group]
                temp = utils.convert(temp)
                temp += '<ul>\n'
                for item in lst:
                    temp += '<li><a href="/monsters/{}">{}</a></li>\n'.format(
                        utils.slug(item.name),
                        item.name,
                    )
                temp += '</ul>\n'
                ret += utils.details_block('<h1>{0}</h1>'.format(group), temp)
        if ret:
            ret = spells.handle_spells(ret, self.get_spell_list(spells.Spells))
            ret = utils.details_group(ret)
        else:
            ret = None
        return ret
