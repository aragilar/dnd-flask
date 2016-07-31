import os
import math
import copy
import re

from . import archiver
from . import utils
from . import spells

class Class (utils.Base):
    combat_proficiencies = []
    description = ''
    equipment = []
    features = []
    hit_die = 8
    long_description = []
    magic = 0
    max_level = 20
    max_slot = 9
    primary_stat = []
    saving_throws = []
    skills = []
    spells = {}
    table = {}
    tool_proficiencies = []
    
    def __str__(self):
        ret = '<div>\n'
    
        # ----#-   Class Description
        temp = '\n'.join(self.long_description)
        temp = utils.convert(temp)
        ret += utils.get_details(temp, 'h1')
    
        # ----#-   Class Details
        
        summary = '<h2>Features</h2>'
        
        short = '<p><strong>Description:</strong> %s</p>\n' % self.description
        
        temp = self.primary_stat[:]
        
        sep = 'and'
        if temp and temp[-1] == '/':
            sep = 'or'
            temp = temp[:-1]
        
        temp = list(map(lambda a: utils.stats[a], temp))
        if len(temp) > 1:
            short += '<p><strong>Primary Abilities:</strong> %s</p>\n' % utils.comma_list(temp, sep)
        elif temp:
            short += '<p><strong>Primary Ability:</strong> %s</p>\n' % temp[0]
        
        short += '<h3>Hit Points</h3>\n'
        
        num = self.hit_die
        if isinstance(num, int):
            num = '1d%d' % num
        
        short += '<p><strong>Hit Dice:</strong> %s</p>\n' % num
        
        num = num.split('d')
        if len(num) == 2 and all(map(str.isdigit, num)):
            die = int(num[1])
            num = int(num[0])
            short += '<p><strong>Hit Points at 1st Level:</strong> %d + your Constitution modifier</p>\n' % (num * die)
            avg = math.ceil((die / 2 + 0.5) * num)
            num = '%dd%d' % (num, die)
            short += (
                '<p><strong>Hit Points at Higher Levels:</strong>'
                ' %s (or %d) + your Constitution modifier per %s level after 1st'
                '</p>\n'
            ) % (num, avg, self.name.lower())
            del avg, die, num
        
        short += '<h3>Proficiencies</h3>\n'
        
        short += '<p><strong>Armor and Weapons:</strong> %s</p>\n' % utils.comma_list(self.combat_proficiencies)
        
        if self.tool_proficiencies:
            temp = utils.choice_list(self.tool_proficiencies)
        else:
            temp = 'None'
        short += '<p><strong>Tools:</strong> %s</p>\n' % temp
        
        temp = self.saving_throws
        temp = list(map(lambda a: utils.stats[a], temp))
        if len(temp) > 1:
            short += '<p><strong>Saving Throws:</strong> %s</p>\n' % utils.comma_list(temp)
        elif temp:
            short += '<p><strong>Saving Throw:</strong> %s</p>\n' % temp[0]
        
        short += '<p><strong>Skills:</strong> %s</p>\n' % utils.choice_list(self.skills)
        
        if self.equipment:
            short += '<h3>Equipment</h3>\n'
            short += '<p>You start with the following equipment in addition to the equipment granted by your background:<p>\n<ul>\n'
            for item in self.equipment:
                short += '<li>%s</li>\n' % self.equipment_row(item)
            short += '</ul>'
        
        group = utils.details_block(summary, short, body_class="class-head")
        group += self.classTable()

        ret += utils.details_group(group)
    
        # ----#-   Class Features
        ret += self.features2html()
        ret += '</div>\n'
    
        ret = spells.handle_spells(ret, self.spell_list)
    
        # ----#-   Subclass
        for subc in self.children.values():
            ret += str(subc)
    
        # ----#-   Class Spells
        temp = self.spell_tables()
        if temp:
            ret += '<div>\n%s</div>\n' % temp
    
        return ret
    
    def classTable(self):
        ret = ''

        if self.table or self.magic > 0:
            if self.magic > 0: # figure out the level of the maximum spell slot
                if self.max_slot != 9:
                    x = self.max_slot
                else:
                    y = self.max_level
                    if y < self.magic:
                        y = 0
                    else:
                        y = int(math.ceil(y / float(self.magic)))
                    for x in range(len(utils.spellslots[-1])):
                        if utils.spellslots[y][x] < 1:
                            break
                    else:
                        x += 1
            else:
                x = 0
            
            headrows = ['Level']
            headrows += self.table.get('@', [])
            if self.magic:
                headrows += ['']
                headrows += list(map(lambda a: utils.ordinals[a], range(1, x + 1)))
            
            body = '<table class="class-table">\n'
            
            if self.magic:
                body += '<caption>%sSpell Slots</caption>\n' % ('&nbsp;' * len(headrows) * 3)
            
            emptycolstyle = ' style="min-width: 0px;"'
            body += '<tr>\n'
            for item in headrows:
                style = ''
                if item == '':
                    style = emptycolstyle
                body += '<th%s>%s</th>\n' % (style, item)
            body += '</tr>\n'
            
            for x in range(1, self.max_level+1):
                body += '<tr>\n'
                for item in headrows:
                    if item != '':
                        body += '<td style="text-align: center;">'
                        if item == 'Level': # character level
                            body += utils.ordinals[x]
                        elif item in self.table: # data specific to the class
                            body += str(self.table.get(item, [])[x-1])
                        elif item[:3] in utils.ordinals: # spell slots
                            if x < self.magic:
                                y = 0
                            else:
                                y = int(math.ceil(x / float(self.magic)))
                            z = utils.ordinals.index(item[:3]) - 1
                            body += str(utils.spellslots[y][z])
                        body += '</td>\n'
                    else:
                        body += '<td%s></td>\n' % emptycolstyle
                body += '</tr>\n'
            body += '</table>'
            ret += utils.details_block('<h2>Table</h2>', body)

        return ret

    def features2html(self):
        ret = ''
        
        lst = copy.deepcopy(self.features)
        if lst:
            data = {}
            if lst and lst[0] and lst[0][0] == 0:
                head = lst.pop(0)
                head.pop(0)
            else:
                head = []
    
            if lst and lst[-1] and lst[-1][0] == -1:
                foot = lst.pop(-1)
                foot.pop(0)
            else:
                foot = []

            if head:
                for item in head:
                    ret += self.feature_block(data, item)
                ret += '<hr>\n'
            
            if lst and all(len(a) and isinstance(a[0], int) for a in lst):
                lst = iter(lst)
                line = next(lst)
                for lvl in range(1, self.max_level+1):
                    while line[0] < lvl:
                        try:
                            line = next(lst)
                        except StopIteration:
                            break
                    
                    if line[0] == lvl:
                        linestr = ''
                        for item in line[1:]:
                            linestr += self.feature_block(data, item)
                    
                        if linestr:
                            ret += '<h2>%s Level</h2>\n' % utils.ordinals[lvl]
                            ret += linestr

            if foot:
                ret += '<hr>\n'
                for item in foot:
                    ret += self.feature_block(data, item)
            
            ret = utils.details_group(ret, body_class="class-features")
        
        return ret
    
    @staticmethod
    def equipment_row(lst):
        if len(lst) > 1:
            ret = []
            for x, item in enumerate(lst):
                short = '('
                short += chr(97 + x)
                short += ') '
                short += item
                ret.append(short)
            return ' or '.join(ret)
        elif lst:
            return str(lst[0])
        else:
            return ''
    
    def feature_block(self, data, feature):
        if isinstance(feature, list):
            temp = feature[1:]
            feature = feature[0]
        else:
            temp = data.get(feature, '')
        
        if isinstance(temp, list):
            temp = '\n'.join(temp)
            temp = utils.convert(temp)
            temp = utils.get_details(temp)
            temp = spells.handle_spells(temp, self.spell_list)
            
            data[feature] = temp
        
        temp = utils.details_block(feature, temp)
        
        return temp
    
    def spell_tables(self):
        table_class = 'spell-table class-spells'
        table_style = 'class="%s"' % table_class
        head_row_style = 'class="head-row"'
        ret = ''
        if self.spells and any(self.spells.values()):
            cantrips = self.spells.get('Cantrip', [])
            if cantrips:
                summary = 'Cantrips'
                body = '<h3 %s>Cantrips</h3>\n' % head_row_style
                temp = ''.join(utils.asyncmap(
                    lambda a: spells.spellblock(a, self.spell_list),
                    list(sorted(cantrips))
                ))
                body += utils.details_group(temp, body_class=table_class)
                ret += utils.details_block(summary, body)

            if self.max_slot > 0 and any(self.spells.get(str(i)) for i in range(1, self.max_slot+1)):
                summary = 'Spells'
                body = ''
                for x in range(1, self.max_slot + 1):
                    if str(x) in self.spells:
                        lst = self.spells[str(x)]
                    else:
                        lst = []
    
                    if lst:
                        body += '<h3 %s>%s-Level Spells</h3>\n' % (head_row_style, utils.ordinals[x])
                        temp = ''.join(utils.asyncmap(
                            lambda a: spells.spellblock(a, self.spell_list),
                            list(sorted(lst))
                        ))
                        body += utils.details_group(temp, body_class=table_class)
                ret += utils.details_block(summary, body)
            ret = utils.details_group(ret)
        return ret
    
    def filter(self, fil):
        ret = super().filter(fil)
        if ret and fil is not None and 'spell' in fil:
            spellfilter = fil['spell']
            for item in ([ret] + list(ret.children.values())):
                item.spells = item.spells.copy()
                for lvl in item.spells.keys():
                    item.spells[lvl] = list(filter(lambda a: spellfilter.get(a), item.spells[lvl]))
        return ret

class SubClass (Class):
    subclass = None
    subclass_spells = {}
    
    def __str__(self):
        ret = '<div>\n'
            
        # ----#-   Features
        summary = '<h1 id="%s">%s</h1>' % (utils.slug(self.name), self.name)
        if self.description:
            body = utils.convert('\n'.join(self.description))
        else:
            body = ''

        group = utils.details_block(summary, body)
        group += self.classTable()

        ret += utils.details_group(group)
        
        ret += self.features2html()
        
        # ----#-   Spells
        ret += self.spell_tables()
        
        ret += '</div>\n'
        
        return ret

Class.subclass = SubClass

class Classes (utils.Group):
    type = Class
    head = '<h1>Classes</h1>\n'
    
    def __init__(self, folder=None, sources=None):
        super().__init__(folder, sources)

        if folder:
            path = os.path.join(folder, 'documentation/classes.md')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = f.read()
                data = utils.convert(data)
                data = utils.get_details(data)
                data = utils.get_details(data, 'h1')
                self.head = data
            
            folder = os.path.join(folder, 'spelllist')
            for c in self:
                for item in ([c] + list(c.children.values())):
                    if isinstance(item.spells, str):
                        spellpath = os.path.join(folder, item.spells + '.json')
                        if os.path.exists(spellpath):
                            item.spells = archiver.load(spellpath)
                        else:
                            item.spells = Class.spells
