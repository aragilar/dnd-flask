import os
import math
import copy
import re
import json

from . import utils
from . import spells

class Class (utils.Base):
    def __init__(self, parent, d):
        for key, value in {
            "magic": 0,
            "max_slot": 9,
            "max_level": 20,
        }.items():
            if d[key] is None:
                d[key] = value

        super().__init__(parent, d)
        self.set_class_spells()

    def set_class_spells(self):
        l = {}
        if self.spell_list_name:
            with self.parent.db as db:
                temp = db.select(
                    "spell_lists",
                    conditions="name='%s'" % (self.spell_list_name.replace("'", "''")),
                )
            if temp:
                l = dict(temp[0])
                for key in l:
                    l[key] = l[key].split("\v") if l[key] else []
                    if l[key]:
                        l[key].pop()
        self.spells = l

    def page(self):
        ret = ''

        # ----#-   Class Description
        if self.description:
            temp = self.description
            temp = utils.convert(temp)
            ret += utils.get_details(temp, 'h1')
        else:
            ret += '<h1>%s</h1>\n' % self.name

        # ----#-   Class Details

        summary = '<h2>Features</h2>'

        if self.summary:
            short = utils.convert('**Description:** %s\n\n' % self.summary)

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

        if self.hit_die:
            short += '<p><strong>Hit Dice:</strong> 1d{0} per {1} level</p>\n'.format(self.hit_die, self.name.lower())

            avg = math.ceil(self.hit_die / 2 + 0.5)
            short += '<p><strong>Hit Points at 1st Level:</strong> %d + your Constitution modifier</p>\n' % (self.hit_die)
            short += (
                '<p><strong>Hit Points at Higher Levels:</strong>'
                ' 1d{} (or {}) + your Constitution modifier per {} level after 1st'
                '</p>\n'
            ).format(self.hit_die, avg, self.name.lower())

        short += '<h3>Proficiencies</h3>\n'

        if self.combat_proficiencies:
            temp = utils.comma_list(self.combat_proficiencies)
        else:
            temp = 'None'
        short += '<p><strong>Armor and Weapons:</strong> %s</p>\n' % temp

        if self.tool_proficiencies:
            temp = utils.choice_list(self.tool_proficiencies)
        else:
            temp = 'None'
        short += '<p><strong>Tools:</strong> %s</p>\n' % temp

        temp = self.saving_throws
        if temp is None:
            temp = []
        temp = list(map(lambda a: utils.stats[a], temp))
        if len(temp) == 1:
            short += '<p><strong>Saving Throw:</strong> %s</p>\n' % temp[0]
        else:
            short += '<p><strong>Saving Throws:</strong> %s</p>\n' % utils.comma_list(temp)

        if self.skills:
            temp = utils.choice_list(self.skills)
        else:
            temp = 'None'
        short += '<p><strong>Skills:</strong> %s</p>\n' % temp

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

        ret = spells.handle_spells(ret, self.parent.get_spell_list(spells.Spells))
        
        ret = '<section class="container">\n%s</section>\n' % ret

        # ----#-   Subclass
        for subc in self.children.values():
            ret += subc.page()

        return ret

    def classTable(self):
        ret = ''

        if self.table_data or self.magic > 0:
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
            if self.table_data:
                headrows += self.table_data.get('@', [])
            if self.magic:
                headrows += ['']
                headrows += list(map(lambda a: utils.ordinals[a], range(1, x + 1)))

            body = '<table class="class-table">\n'

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
                        elif self.table_data and item in self.table_data:
                            # data specific to the class
                            body += str(self.table_data.get(item, [])[x-1])
                        elif item[:3] in utils.ordinals:
                            # spell slots
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
                            ret += '<b>%s Level</b>\n' % utils.ordinals[lvl]
                            ret += linestr

            if foot or any(self.spells.values()):
                ret += '<hr>\n'
            if foot:
                for item in foot:
                    ret += self.feature_block(data, item)

            ret += self.spell_tables()

            ret = utils.details_group(ret)

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
            temp = spells.handle_spells(temp, self.parent.get_spell_list(spells.Spells))

            data[feature] = temp

        temp = utils.details_block(feature, temp)

        return temp

    def spell_tables(self):
        spell_list = self.parent.get_spell_list(spells.Spells).dict()
        table_class = 'spell-table class-spells'
        table_style = 'class="%s"' % table_class
        head_row_style = 'class="head-row"'
        ret = ''
        if any(self.spells.values()):
            cantrips = self.spells.get('cantrips', [])
            if cantrips:
                summary = 'Cantrips'
                body = '<h3 %s>Cantrips</h3>\n' % head_row_style
                temp = ''.join(utils.asyncmap(
                    lambda a: spells.spellblock(a, spell_list),
                    list(sorted(cantrips))
                ))
                body += utils.details_group(temp, body_class=table_class)
                ret += utils.details_block(summary, body)

            levelname = "level_%d_spells".__mod__
            if self.max_slot > 0 and any(self.spells.get(levelname(i)) for i in range(1, self.max_slot+1)):
                summary = 'Spells'
                body = ''
                for x in range(1, self.max_slot + 1):
                    if levelname(x) in self.spells:
                        lst = self.spells[levelname(x)]
                    else:
                        lst = []

                    if lst:
                        body += '<h3 %s>%s-Level Spells</h3>\n' % (head_row_style, utils.ordinals[x])
                        temp = ''.join(utils.asyncmap(
                            lambda a: spells.spellblock(a, spell_list),
                            list(sorted(lst))
                        ))
                        body += utils.details_group(temp, body_class=table_class)
                ret += utils.details_block(summary, body)
            #ret = utils.details_group(ret)
        return ret

class SubClass (Class):
    def __init__(self, parent, d):
        for key, value in {
            "magic": 0,
            "max_slot": 9,
            "max_level": 20,
        }.items():
            if d[key] is None:
                d[key] = value

        utils.Base.__init__(self, parent, d)
        self.set_class_spells()

    def page(self):
        ret = ''

        # ----#-   Features
        summary = '<h1 id="%s">%s</h1>' % (utils.slug(self.name), self.name)
        if self.description:
            body = utils.convert(self.description)
        else:
            body = ''

        group = utils.details_block(summary, body)
        group += self.classTable()

        ret += utils.details_group(group)

        ret += self.features2html()

        ret = '<section class="container">\n%s</section>\n' % ret

        return ret

class Classes (utils.Group):
    type = Class
    subtype = SubClass
    tablename = "classes"
    
    @property
    def head(self):
        return self.get_document("Classes", "Classes")
