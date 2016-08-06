import os
import urllib.parse

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
    challenge_rating = None
    condition_immunities = []
    damage_immunities = []
    damage_resistances = []
    description = []
    experience = 0
    hit_points = '3 (1d4)'
    languages = []
    legendary_actions = []
    saving_throws = {}
    senses = []
    size = 'Medium'
    skills = {}
    speed = '30 ft.'
    traits = []
    type = 'beast'
    
    group = None
    _page = None
    
    def dict(self):
        d = {
            'name': self.name,
            'alignment': self.alignment,
            'challenge rating': self._get_cr(),
            'legendary': bool(self.legendary_actions),
            'size': self.size,
            'type': self.type,
        }
        return d
    
    def _get_cr(self):
        if self.challenge_rating is None:
            c = challenge_ratings.get(self.experience, -1)
        else:
            c = self.challenge_rating
        c = float(c)
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
    
    def __str__(self):
        if self._page is None:
            ret = ''
            
            ret += utils.details_group(utils.details_block(
                '<h1>%s</h1>\n' % self.name,
                utils.convert('\n'.join(self.description)),
            ))
            
            ret += '<div class="monster-box">\n'
            ret += '<h1>%s</h1>\n' % self.name
            ret += '<p><em>{size} {type}, {alignment}</em></p>\n'.format(
                alignment=self.alignment,
                size=self.size,
                type=self.type,
            )
            ret += '<hr>\n'
            ret += '<p><strong>Armor Class</strong> %s</p>\n' % self.armor_class
            ret += '<p><strong>Hit Points</strong> %s</p>\n' % self.hit_points
            ret += '<p><strong>Speed</strong> %s</p>\n' % self.speed
            ret += '<hr>\n'
            
            ret += '<ul class="monster-stats">\n'
            for stat in utils.stats:
                value = self.ability_scores.get(stat, 10)
                ret += '<li><strong>{}</strong> {} ({:+})</li>\n'.format(stat.upper(), value, utils.get_modifier(value))
            ret += '</ul>\n'
            
            ret += '<hr>\n'
            
            if self.saving_throws:
                ret += '<p><strong>Saving Throws</strong> %s</p>\n' % ', '.join(
                    '{} {:+}'.format(stat, self.saving_throws[stat])
                    for stat in map(str.title, utils.stats)
                    if stat in self.saving_throws
                )
            
            if self.skills:
                ret += '<p><strong>Skills</strong> %s</p>\n' % ', '.join(
                    '{} {:+}'.format(skill, self.skills[skill])
                    for skill in sorted(self.skills)
                )
            
            if self.damage_resistances:
                sep = ', '
                if any(',' in a for a in self.damage_resistances):
                    sep = '; '
                ret += '<p><strong>Damage Resistances</strong> %s</p>\n' % sep.join(
                    self.damage_resistances
                )
            
            if self.damage_immunities:
                sep = ', '
                if any(',' in a for a in self.damage_immunities):
                    sep = '; '
                ret += '<p><strong>Damage Immunities</strong> %s</p>\n' % sep.join(
                    self.damage_immunities
                )
            
            if self.condition_immunities:
                ret += '<p><strong>Condition Immunities</strong> %s</p>\n' % ', '.join(
                    self.condition_immunities
                )
            
            if self.senses:
                ret += '<p><strong>Senses</strong> %s</p>\n' % ', '.join(
                    self.senses
                )
            
            if self.languages:
                temp = ', '.join(self.languages)
            else:
                temp = '-'
            ret += '<p><strong>Languages</strong> %s</p>\n' % temp
            
            ret += '<p><strong>Challenge</strong> {} ({:,} XP)</p>\n'.format(self.get_cr(), self.experience)
            
            ret += '<hr>\n'
            
            for item in self.traits:
                ret += utils.convert('***{}.*** {}'.format(item[0], '\n'.join(item[1:])))
            
            if self.actions:
                ret += '<h2>Actions</h2>\n'
                for item in self.actions:
                    ret += utils.convert('***{}.*** {}'.format(item[0], '\n'.join(item[1:])))
            
            if self.legendary_actions:
                ret += '<h2>Actions</h2>\n'
                desc = 0
                while isinstance(self.legendary_actions[desc], str):
                    desc += 1
                temp = self.legendary_actions[desc:]
                desc = self.legendary_actions[:desc]
                
                if desc:
                    ret += utils.convert('\n'.join(desc))
                
                for item in temp:
                    ret += utils.convert('**{}.** {}'.format(item[0], '\n'.join(item[1:])))
            
            ret += '</div>\n'
            
            ret = spells.handle_spells(ret, self.spell_list)
            ret = '<div>\n%s</div>\n' % ret
            
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
        ret = '<li><a href="{0}">{0}</a></li>\n'.format(name)
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
        <div style="padding: 5px; margin: 5px auto;">
        
        <h2>Search</h2>
        
        </div>
        '''

        temp = ''.join(utils.asyncmap(
            monsterblock,
            self.values(),
        ))
        ret += utils.details_group(temp, body_id="monsters", body_class="spell-table")
        
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
            temp = self.groups[group]
            temp = utils.convert(temp)
            lst = []
            for item in self.values():
                if item.group == group:
                    lst.append(item)
            if lst:
                temp += '<ul>\n'
                for item in lst:
                    temp += '<li><a href="../monsters/{}">{}</a></li>\n'.format(
                        urllib.parse.quote(item.name),
                        item.name,
                    )
                temp += '</ul>\n'
                ret += utils.details_block('<h1>%s</h1>' % group, temp)
        if ret:
            ret = utils.details_group(ret)
            ret = '<div>\n%s</div>\n' % ret
        else:
            ret = None
        return ret
