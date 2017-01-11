import os
import math
import copy
import re
from collections import OrderedDict, defaultdict

from . import utils
from . import spells

class Class (utils.Base):
    @property
    def max_level(self):
        if self._max_level is None:
            self._max_level = 20
        return self._max_level
    
    @max_level.setter
    def max_level(self, max_level):
        self._max_level = max_level
    
    @property
    def max_slot(self):
        if self.max_slot is None and self.magic:
            slot_level = spell_slot_level(self.magic, self.max_level)
            for max_slot in range(len(utils.spellslots[slot_level])):
                if utils.spellslots[slot_level][max_slot] < 1:
                    break
            else:
                max_slot += 1
            self._max_slot = max_slot
        else:
            max_slot = self._max_slot
        return x
    
    @max_slot.setter
    def max_slot(self, max_slot):
        if max_slot is None:
            max_slot = 0
        self._max_slot = max_slot

    @property
    def spells(self):
        if not hasattr(self, "_spells"):
            l = defaultdict(list)
            if self.spell_list_name:
                with self.parent.db as db:
                    temp = db.select(
                        ["spell_lists L", "spells S"],
                        columns=[
                            "L.spell",
                            "S.level",
                        ],
                        conditions=[
                            "L.class='%s'" % (self.spell_list_name.replace("'", "''")),
                            "L.spell=S.name",
                        ],
                        order=["L.spell"],
                    )
                if temp:
                    for spell in temp:
                        if spell["level"] == 0:
                            level = "cantrips"
                        else:
                            level = str(spell["level"])
                        l[level].append(spell["spell"])
            self._spells = l
        return self._spells

    def page(self):
        ret = '<h1>%s</h1>' % self.name

        # ----#-   Class Description
        if self.description:
            temp = self.description
            temp = utils.convert(temp)
            ret = utils.details_block(ret, temp)

        # ----#-   Class Details
        if self.summary:
            short = '**Description:** %s\n\n' % self.summary

        temp = self.primary_stat[:]

        sep = 'and'
        if temp and temp[-1] == '/':
            sep = 'or'
            temp = temp[:-1]

        temp = list(map(lambda a: utils.stats[a], temp))
        if len(temp) > 1:
            short += '**Primary Abilities:** %s\n\n' % utils.comma_list(temp, sep)
        elif temp:
            short += '**Primary Ability:** %s\n\n' % temp[0]

        short += '### Hit Points\n\n'

        if self.hit_die:
            short += '**Hit Dice:** 1d{0} per {1} level\n\n'.format(self.hit_die, self.name.lower())

            avg = math.ceil(self.hit_die / 2 + 0.5)
            short += '**Hit Points at 1st Level:** %d + your Constitution modifier\n\n' % (self.hit_die)
            short += '**Hit Points at Higher Levels:** 1d%d (or %d) + your Constitution modifier per %s level after 1st\n\n' % (self.hit_die, avg, self.name.lower())

        short += '### Proficiencies\n\n'

        if self.combat_proficiencies:
            temp = utils.comma_list(self.combat_proficiencies)
        else:
            temp = 'None'
        short += '**Armor and Weapons:** %s\n\n' % temp

        if self.tool_proficiencies:
            temp = utils.choice_list(self.tool_proficiencies)
        else:
            temp = 'None'
        short += '**Tools:** %s\n\n' % temp

        temp = self.saving_throws
        if temp is None:
            temp = []
        temp = list(map(lambda a: utils.stats[a], temp))
        if len(temp) == 1:
            short += '**Saving Throw:** %s\n\n' % temp[0]
        else:
            short += '**Saving Throws:** %s\n\n' % utils.comma_list(temp)

        if self.skills:
            temp = utils.choice_list(self.skills)
        else:
            temp = 'None'
        short += '**Skills:** %s\n\n' % temp

        if self.equipment:
            short += '### Equipment\n\n'
            short += 'You start with the following equipment in addition to the equipment granted by your background:\n\n'
            for item in self.equipment:
                short += '* %s\n' % self.equipment_row(item)
        short = utils.convert(short)

        ret += utils.details_block('<h2>Features</h2>', short, body_class="class-head")
        ret += self.classTable()

        ret = utils.details_group(ret)

        # ----#-   Class Features
        ret += self.features2html()

        ret = spells.handle_spells(ret, self.parent.get_spell_list(spells.Spells))

        ret = '<section class="container">\n%s</section>\n' % ret

        # ----#-   Subclass
        if self.children:
            for subc in self.children.values():
                ret += subc.page()

        return ret

    def classTable(self):
        ret = ''

        if self.table_data or self.magic:
            headrows = ['Level']
            if self.table_data:
                headrows.extend(self.table_data.keys())
            if self.magic:
                headrows.append('')
                headrows.extend(map(lambda a: utils.ordinals[a], range(1, self.max_slot + 1)))

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
                            y = spell_slot_level(self.magic, x)
                            z = utils.ordinals.index(item[:3]) - 1
                            slots = str(utils.spellslots[y][z])
                            if slots == '0':
                                slots = '-'
                            body += slots
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

            if self.max_slot and any(self.spells.get(str(i)) for i in range(1, self.max_slot+1)):
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

def spell_slot_level(magic, level):
    if not magic:
        y = 0
    elif x < magic:
        y = 0
    else:
        y = int(math.ceil(level / float(magic)))
    return y

class Classes (utils.Group):
    type = Class
    subtype = SubClass
    singular = "Class"
    plural = "Classes"
    tables = [
    {
        "table": "sub" + plural,
        "fields": OrderedDict([
            ("class", str),
            ("name", str),
            ("source", str),
            ("sort_index", int),
            ("description", str),
            ("table_data", str),
            ("magic", int),
            ("max_slot", int),
            ("max_level", int),
            ("features", str),
            ("spell_list_name", str),
        ]),
        "constraints": {
            "class": "REFERENCES %s(name)" % plural,
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
        }
    },
    {
        "table": plural,
        "fields": OrderedDict([
            ("name", str),
            ("source", str),
            ("sort_index", int),
            ("prestige", int),
            ("description", str),
            ("summary", str),
            ("primary_stat", str),
            ("hit_die", int),
            ("combat_proficiencies", str),
            ("tool_proficiencies", str),
            ("saving_throws", str),
            ("skills", str),
            ("equipment", str),
            ("table_data", str),
            ("magic", int),
            ("max_slot", int),
            ("max_level", int),
            ("features", str),
            ("spell_list_name", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
        }
    }
    ]

    @property
    def head(self):
        return self.get_document("Classes", "Classes")
