import os

from . import archiver
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
    ability_scores = {}
    actions = []
    alignment = 'unaligned'
    armor_class = '10'
    challenge_description = '{cr} ({xp} XP)'
    challenge_rating = None
    condition_immunities = []
    damage_immunities = []
    damage_resistances = []
    damage_vulnerabilities = []
    description = []
    experience = 0
    hit_points = '3 (1d4)'
    languages = []
    legendary_actions = []
    reactions = []
    saving_throws = {}
    senses = []
    size = 'Medium'
    skills = {}
    speed = ['30 ft.']
    traits = []
    type = 'beast'

    group = None
    _page = None

    def dict(self):
        d = {
            'name': self.name,
            'alignment': self.alignment.lower(),
            'challenge rating': self._get_cr(),
            'legendary': bool(self.legendary_actions),
            'size': self.size.lower(),
            'type': self.type.lower(),
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

    def page(self):
        if self._page is None:
            ret = ''

            if self.description or self.group:
                temp = '\n'.join(self.description)
                if self.group:
                    if not temp:
                        temp = '# {}'.format(self.group)
                    temp += '\n\n***\n\nThis monster is a member of the {0} [group](/monsters/groups/).'.format(self.group)
                temp = utils.convert(temp)
                if not temp.startswith('<h1'):
                    temp = '<h1>{}</h1>\n'.format(self.name) + temp
                ret += utils.get_details(temp, 'h1')

            ret += '<div class="monster-box">\n'

            md = '# {}\n\n'.format(self.name)
            md += '*{size} {type}, {alignment}*\n\n'.format(
                alignment=self.alignment,
                size=self.size,
                type=self.type,
            )
            md += '***\n\n'
            md += '**Armor Class** {}\n\n'.format(self.armor_class)
            md += '**Hit Points** {}\n\n'.format(self.hit_points)
            md += '**Speed** {}\n\n'.format(', '.join(self.speed))
            md += '***\n\n'

            for stat in utils.stats:
                value = self.ability_scores.get(stat, 10)
                md += '* **{}** {} ({:+})\n'.format(stat.upper(), value, utils.get_modifier(value))

            md += '\n***\n\n'

            if self.saving_throws:
                md += '**Saving Throws** {}\n\n'.format(', '.join(
                    '{} {:+}'.format(stat, self.saving_throws[stat])
                    for stat in map(str.title, utils.stats)
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

            temp = self.senses.copy()
            if not any(item.startswith('passive Perception ') for item in temp):
                if 'Perception' in self.skills:
                    s = self.skills['Perception']
                else:
                    s = utils.get_modifier(self.ability_scores['wis'])
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

            md += '***\n\n'

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

            md = utils.convert(md)
            md = md.replace('<ul>', '<ul class="monster-stats">', 1)
            ret += md

            ret += '</div>\n'

            ret = spells.handle_spells(ret, self.spell_list)
            ret = '<div>\n{}</div>\n'.format(ret)

            self._page = ret
        else:
            ret = self._page

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
    javascript = ['monsters.js']

    head = '<h1>Monsters</h1>\n'

    def __init__(self, folder=None, sources=None):
        super().__init__(folder, sources)
        self.groups = {}
        if folder:
            path = os.path.join(folder, 'documentation/monsters.md')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = f.read()
                data = utils.convert(data)
                data = utils.get_details(data, splttag='h1')
                data = utils.get_details(data, 'h1')
                self.head = data

            path = os.path.join(folder, self.type.__name__.lower())
            if os.path.exists(path):
                for file in os.listdir(path):
                    file = os.path.join(path, file)
                    if file.endswith('.md'):
                        with open(file, 'r') as f:
                            temp = f.readlines()
                        self.groups[temp[0].lstrip('#').strip()] = (
                            ''.join(temp[2:])
                            if len(temp) > 1
                            else ''
                        )

            for item in self.values():
                if item.group and item.group not in self.groups:
                    self.groups[item.group] = ''

    def page(self):
        itemscopy = {}
        for item in self.values():
            itemscopy[item.name] = item.dict()

        ret = '<script>\nmonsters = %s;\n</script>\n' % (archiver.p(itemscopy, compact=True))

        ret += self.head

        ret += '''
        <div class="search-box">
        <h2>Search</h2>
        <p>
            Name: <input class="filter" id="name">
            <br>
            Type: <input class="filter" id="type">
        </p>
        <p>
            Min CR <input class="filter" id="crge">
            <br>
            Max CR <input class="filter" id="crle">
        </p>
        <p class="right">
            <label><input type="checkbox" class="filter size" id="tiny"> Tiny </label>
            <br>
            <label><input type="checkbox" class="filter size" id="small"> Small</label>
            <br>
            <label><input type="checkbox" class="filter size" id="medium"> Medium</label>
            <br>
            <label><input type="checkbox" class="filter size" id="large"> Large</label>
            <br>
            <label><input type="checkbox" class="filter size" id="huge"> Huge</label>
            <br>
            <label><input type="checkbox" class="filter size" id="gargantuan"> Gargantuan</label>
        </p>
        <p><label><input type="checkbox" class="filter" id="legendary"> Legendary</label></p>
        <p>Count: <output id="count">0</output></p>
        </div>
        '''

        temp = ''.join(utils.asyncmap(
            monsterblock,
            self.values(),
        ))
        ret += '<ul id="monsters" class="spell-table">\n%s</ul>\n' % temp

        ret = '<div>\n%s</div>\n' % ret
        return ret

    def filter(self, f=None):
        new = super().filter(f)
        new.groups = new.groups.copy()
        for group in list(new.groups.keys()):
            if not any(item.group == group for item in new.values()):
                del new.groups[group]
        return new

    def groups_page(self):
        ret = ''
        for group in sorted(self.groups):
            lst = []
            for item in self.values():
                if item.group == group:
                    lst.append(item)
            if lst:
                temp = self.groups[group]
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
            ret = spells.handle_spells(ret, self.spell_list)
            ret = utils.details_group(ret)
            ret = '<div>\n%s</div>\n' % ret
        else:
            ret = None
        return ret
