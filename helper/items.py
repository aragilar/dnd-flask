import os
import re

from . import archiver
from . import utils

class Weapon (utils.Base):
    cost = 0.0
    damage = ''
    damage_type = 'unknown'
    properties = ['-']
    ranged = False
    weight = '0'

    special = ''

    def __str__(self):
        ret = '<tr>\n'
        
        ret += '<th>%s</th>\n' % self.name
        
        if self.cost > 0:
            if self.cost < 0.1:
                ret += '<td>%d cp</td>\n' % int(self.cost * 100)
            elif self.cost < 1:
                ret += '<td>%d sp</td>\n' % int(self.cost * 10)
            else:
                ret += '<td>%d gp</td>\n' % int(self.cost)
        else:
            ret += '<td>-</td>\n'
        
        ret += '<td>%s %s</td>' % (self.damage, self.damage_type)
        ret += '<td>%s lb.</td>\n' % self.weight
        ret += '<td>%s</td>\n' % ', '.join(self.properties)
        
        ret += '</tr>\n'
        return ret

class Weapons (utils.Group):
    type = Weapon

    def page(self, load):
        temp = ''
        t = load('weapons.md')
        if t:
            temp += t
            temp += '\n\n'
        else:
            temp += '<h1>Weapons</h1>\n'
        del t
        
        temp += '## Special\n\n'
        for item in self.values():
            if item.special:
                temp += '**%s** %s\n\n' % (item.name, item.special)
        temp = utils.get_details(utils.convert(temp))
        
        temp += '<table id="weapons-table">\n'
        temp += '<tr><th>Name</th><th>Cost</th><th>Damage</th><th>Weight</th><th>Properties</th></tr>'
        martial_melee = []
        martial_ranged = []
        simple_melee = []
        simple_ranged = []
        other = []
        for weapon in self:
            if weapon.type == 'martial':
                if not weapon.ranged:
                    martial_melee.append(weapon)
                else:
                    martial_ranged.append(weapon)
            elif weapon.type == 'simple':
                if not weapon.ranged:
                    simple_melee.append(weapon)
                else:
                    simple_ranged.append(weapon)
            else:
                other.append(weapon)
        
        for name, lst in [('Simple Melee', simple_melee), ('Simple Ranged', simple_ranged), ('Martial Melee', martial_melee), ('Martial Ranged', martial_ranged), ('Other', other)]:
            if lst:
                temp += '<tr><th colspan="5">%s</th></tr>\n' % name
                for weapon in lst:
                    temp += str(weapon)
        
        temp += '</table>\n'
        return utils.get_details(temp, 'h1')

class Armor (utils.Base):
    ac = '-'
    cost = 0.0
    note = '-'
    stealth = False
    strength = 0
    weight = '0'

    def __str__(self):
        ret = '<tr>\n'
        
        ret += '<th>%s</th>' % self.name
        
        if self.cost > 0:
            if self.cost < 0.1:
                ret += '<td>%d cp</td>\n' % int(self.cost * 100)
            elif self.cost < 1:
                ret += '<td>%d sp</td>\n' % int(self.cost * 10)
            else:
                ret += '<td>%d gp</td>\n' % int(self.cost)
        else:
            ret += '<td>-</td>\n'
        
        ret += '<td>%s</td>\n' % self.ac
        
        if self.strength:
            ret += '<td>%d</td>\n' % self.strength
        else:
            ret += '<td>-</td>\n'
        
        if self.stealth:
            ret += '<td>Disadvantage</td>\n'
        else:
            ret += '<td>-</td>\n'
        
        ret += '<td>%s</td>\n' % self.weight
        ret += '<td>%s</td>\n' % self.note
        
        ret += '</tr>\n'
        return ret

class Armors (utils.Group):
    type = Armor

    def page(self, load):
        temp = ''
        t = load('armors.md')
        if t:
            temp += t
            temp += '\n\n'
        else:
            temp += '<h1>Armors</h1>\n'
        del t
        temp = utils.get_details(utils.convert(temp))
        
        temp += '<table id="armor-table">\n'
        temp += '<tr><th>Armor</th><th>Cost</th><th>Armor Class (ac)</th><th>Strength</th><th>Stealth</th><th>Weight</th><th>Note</th></tr>'
        light = []
        medium = []
        heavy = []
        other = []
        alist = self.values()
        alist = sorted(alist, key=lambda a: not a.stealth)
        alist = sorted(alist, key=lambda a: a.ac)
        alist = sorted(alist, key=lambda a: a.cost if a.cost else float('inf'))
        for armor in alist:
            type = armor.type
            if type == 'light':
                light.append(armor)
            elif type == 'medium':
                medium.append(armor)
            elif type == 'heavy':
                heavy.append(armor)
            else:
                other.append(armor)
        
        for name, lst in [('Light', light), ('Medium', medium), ('Heavy', heavy), ('Other', other)]:
            if lst:
                temp += '<tr><th colspan="7">%s</th></tr>\n' % name
                for armor in lst:
                    temp += str(armor)
        temp += '</table>\n'
        return utils.get_details(temp, 'h1')

class Item (utils.Base):
    cost = 0.0
    description = ''
    group = None
    weight = '-'

    def __str__(self):
        temp = self.description
        if temp:
            temp = utils.convert(str(temp))

        ret = '<td>'
        ret += utils.details_group(utils.details_block(self.name, temp))
        ret += '</td>\n'
        
        if isinstance(self.cost, str):
            ret += '<td>-</td>\n'
        elif self.cost > 0:
            if self.cost < 0.1:
                ret += '<td>%d cp</td>\n' % int(self.cost * 100)
            elif self.cost < 1:
                ret += '<td>%d sp</td>\n' % int(self.cost * 10)
            else:
                ret += '<td>%d gp</td>\n' % int(self.cost)
        else:
            ret += '<td>-</td>\n'
        
        ret += '<td>%s</td>\n' % self.weight
        
        ret = '<tr>%s</tr>\n' % ret

        return ret

class Items (utils.Group):
    type = Item

    def __init__(self, folder=None, sources=None):
        super().__init__(folder, sources)
        self.groups = {}
        if folder:
            t = os.path.join(folder, self.type.__name__.lower())
            if os.path.exists(t):
                folder = t
                for item in os.listdir(folder):
                    item = os.path.join(folder, item)
                    if os.path.isfile(item) and item.endswith('.md'):
                        with open(item, 'r') as f:
                            temp = f.readlines()
                        temp = {
                            'name': temp[0].lstrip('#').strip(),
                            'description': (
                                ''.join(temp[2:])
                                if len(temp) > 1
                                else ''
                            ),
                        }
                        self.add(temp)
    
    def add(self, item):
        if isinstance(item, self.type):
            super().add(item)
        elif isinstance(item, dict):
            g = item['name']
            g = self._getgroup(g)
            if g is not None:
                self.groups[g] = item['description']
    
    @staticmethod
    def _getgroup(g):
        if g is not None:
            g = g.split('/')
            if g:
                g = g[-1]
            else:
                g = ''
        return g

    def page(self, load):
        ret = load('equipment.md')
        if ret:
            ret = utils.convert(ret)
            ret = utils.get_details(ret)
        else:
            ret = '<h1>Equipment</h1>\n'
        
        ret += '<table>\n'
        ret += (
            '<tr>'
            '<th>Item</th>'
            '<th>Cost</th>'
            '<th>Weight</th>'
            '</tr>\n'
        )
        
        for item in self.values():
            if not item.group:
                ret += str(item)
        
        ret += '</table>\n'
        
        for name in sorted(self.groups):
            description = self.groups[name]
            hadany = False
            temp = '<h2>%s</h2>\n' % name
            temp += utils.convert(description)
            temp += '<table>\n'
            temp += (
                '<tr>'
                '<th>Item</th>'
                '<th>Cost</th>'
                '<th>Weight</th>'
                '</tr>\n'
            )
            for item in self.values():
                if self._getgroup(item.group) == name:
                    temp += str(item)
                    hadany = True
            temp += '</table>\n'
            if hadany:
                ret += utils.get_details(temp)
        
        ret = utils.get_details(ret, 'h1')
        
        return ret

def main(weapons, armors, items, load):
    ret = '<div id="items-div">\n'
    
    if items:
        ret += items.page(load)
    
    temp = load('equipment-packs.md')
    if temp:
        ret += utils.get_details(utils.get_details(utils.convert(temp)), 'h1')
    
    if weapons:
        ret += weapons.page(load)
    
    if armors:
        ret += armors.page(load)
    
    ret += '</div>\n'
    return ret
