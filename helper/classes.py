import math
import copy
import re
from . import utils
from . import spells as spellmod

def feature_block(data, feature):
    if isinstance(feature, list):
        temp = feature[1:]
        feature = feature[0]
    else:
        temp = data.get(feature, '')
    
    if isinstance(temp, list):
        temp = '\n'.join(temp)
        temp = utils.convert(temp)
        temp = utils.get_details(temp)
        #temp = re.sub('<h2.*?>', '', temp)
        #temp = temp.replace('</h2>', '')
        
        data[feature] = temp
    
    temp = utils.details_block(feature, temp)
    
    return temp

def spell_tables(spells, maxslot, spell_list):
    table_class = 'spell-table class-spells'
    table_style = 'class="%s"' % table_class
    head_row_style = 'class="head-row"'
    ret = ''
    if spells != None and any(spells.values()):
        print(spells.values())
        cantrips = spells.get('Cantrip', [])
        if cantrips:
            summary = 'Cantrips'
            body = '<table %s>\n' % table_style
            body += '<tr><th %s>Cantrips</th></tr>\n<tr><td>\n' % head_row_style
            body += '\n</td></tr>\n<tr><td>\n'.join(utils.asyncmap(
                lambda a: spellmod.spellblock(a, spell_list),
                list(sorted(filter(lambda a: a in spell_list, cantrips)))
            ))
            body += '</td></tr>\n</table>'
            body = utils.details_group(body, body_class=table_class)
            ret += utils.details_group(utils.details_block(summary, body))

        if maxslot > 0 and any(spells.get(str(i)) for i in range(1, maxslot+1)):
            summary = 'Spells'
            body = '<table %s>\n' % table_style
            for x in range(1, maxslot + 1):
                if str(x) in spells:
                    lst = spells[str(x)]
                else:
                    lst = []

                if len(lst):
                    body += '<tr><th %s>%s-Level Spells</th></tr>\n<tr><td>\n' % (head_row_style, utils.ordinals[x])
                    body += '\n</td></tr>\n<tr><td>\n'.join(utils.asyncmap(
                        lambda a: spellmod.spellblock(a, spell_list),
                        list(sorted(filter(lambda a: a in spell_list, lst)))
                    ))
            body += '\n</td></tr>\n</table>'
            body = utils.details_group(body, body_class=table_class)
            ret += utils.details_group(utils.details_block(summary, body))
    return ret

def features2html(c):
    lst = copy.deepcopy(c.get('features', []))
    data = c.get('features-data', {})
    ret = ''
    maxlevel = c.get("max-level", 20)
    
    # ----#-   Table
    table = c.get('table')
    magic = c.get('magic', 0)
    if table != None or magic > 0:
        if table == None:
            table = {}
        
        if magic > 0: # figure out the level of the maximum spell slot
            if 'max-slot' in c:
                x = c['max-slot']
            else:
                y = maxlevel
                if y < magic:
                    y = 0
                else:
                    y = int(math.ceil(y / float(magic)))
                for x in range(len(utils.spellslots[-1])):
                    if utils.spellslots[y][x] < 1:
                        break
                else:
                    x += 1
        else:
            x = 0
        
        headrows = ['Level']
        headrows += table.get('@', [])
        if magic:
            headrows += ['']
            headrows += list(map(lambda a: utils.ordinals[a], range(1, x + 1)))
        
        body = '<table class="class-table">\n'
        
        if magic:
            body += '<caption>%sSpell Slots</caption>\n' % ('&nbsp;' * len(headrows) * 3)
        
        emptycolstyle = ' style="min-width: 0px;"'
        body += '<tr>\n'
        for item in headrows:
            style = ''
            if item == '':
                style = emptycolstyle
            body += '<th%s>%s</th>\n' % (style, item)
        body += '</tr>\n'
        
        for x in range(1, maxlevel+1):
            body += '<tr>\n'
            for item in headrows:
                if item != '':
                    body += '<td style="text-align: center;">'
                    if item == 'Level': # character level
                        body += utils.ordinals[x]
                    elif item in table: # data specific to the class
                        body += str(table.get(item, [])[x-1])
                    elif item[:3] in utils.ordinals: # spell slots
                        if x < magic:
                            y = 0
                        else:
                            y = int(math.ceil(x / float(magic)))
                        z = utils.ordinals.index(item[:3]) - 1
                        body += str(utils.spellslots[y][z])
                    body += '</td>\n'
                else:
                    body += '<td%s></td>\n' % emptycolstyle
            body += '</tr>\n'
        body += '</table>'
        ret += utils.details_block('Table', body)
    
    # ----#-   Features
    if len(lst):
        if lst[0] and lst[0][0] == 0:
            head = lst.pop(0)
            head.pop(0)
        else:
            head = []

        if lst[-1] and lst[-1][0] == -1:
            foot = lst.pop(-1)
            foot.pop(0)
        else:
            foot = []

        for item in head:
            ret += feature_block(data, item)
        
        ret += '<ol>\n'
        lst = iter(lst)
        line = next(lst)
        for lvl in range(1, maxlevel+1):
            while line[0] < lvl:
                try:
                    line = next(lst)
                except StopIteration:
                    break
            
            linestr = ''
            if line[0] == lvl:
                for item in line[1:]:
                    linestr += feature_block(data, item)
            
            ret += '<li>%s</li>\n' % linestr
        ret += '</ol>\n'

        for item in foot:
            ret += feature_block(data, item)
        
        ret = utils.details_group(ret)#, body_class="class-features")
    return ret

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
    elif len(lst) == 1:
        return str(lst[0])
    else:
        return ''

def class2html(c, spell_list):
    ret = ''
    ret += '<div>\n'
    #ret += '<h1>%s</h1>\n' % c.get('name', '')

    # ----#-   Class Description
    temp = c.get('longdescription', '')
    temp = '\n'.join(temp)
    temp = utils.convert(temp)
    temp = utils.get_details(temp, 'h1')
    ret += temp
    ret += '</div>\n\n'

    # ----#-   Class Details
    ret += '<div>\n'
    summary = '<h2>Features</h2>'
    
    short = '**Description:** %s\n\n' % c.get('description', '')
    short += '###### Hit Points\n\n'
    short += '**Hit Die:** %s\n\n' % c.get('hit die', '')
    short += '###### Proficiencies\n\n'
    temp = c.get('primary stat', [])
    sep = 'and'
    if temp[-1] == '/':
        sep = 'or'
        temp = temp[:-1]
    temp = list(map(lambda a: utils.stats[a], temp))
    if len(temp) > 1:
        short += '**Primary Abilities:** %s\n\n' % utils.comma_list(temp, sep)
    elif len(temp) == 1:
        short += '**Primary Ability:** %s\n\n' % temp[0]
    temp = c.get('saving throws', [])
    temp = list(map(lambda a: utils.stats[a], temp))
    if len(temp) > 1:
        short += '**Saving Throw Proficiencies:** %s\n\n' % utils.comma_list(temp)
    elif len(temp) == 1:
        short += '**Saving Throw Proficiency:** %s\n\n' % temp[0]
    short += '**Armor and Weapon Proficiencies:** %s\n\n' % utils.comma_list(c.get('combat proficiencies', []))
    temp = utils.choice_list(c.get('tool proficiencies', []))
    if temp != 'none':
        short += '**Tool Proficiencies:** %s\n\n' % temp
    short += '**Skills:** %s\n\n' % utils.choice_list(c.get('skills', []))
    temp = c.get('equipment', [])
    if len(temp):
        short += '###### Equipment\n\n'
        short += 'You start with the following equipment in addition to the equipment granted by your background:\n\n'
        for item in temp:
            short += '* %s\n' % equipment_row(item)
    short = utils.convert(short)
    
    ret += utils.details_block(summary, short, body_class="class-head")

    # ----#-   Class Features
    ret += features2html(c)
    ret += '</div>\n'

    # ----#-   Subclass
    subclassdict = c.get('subclass', {})
    for name in subclassdict:
        subc = subclassdict[name]
        subcstr = '\n<div>\n\n'
        
        # ----#-   Subclass Features
        n = subc.get('name', '')
        desc = subc.get('description')
        summary = '<h2 id="%s">%s</h2>' % (utils.slug(n), n)
        body = utils.convert('\n'.join(desc))
        if body:
            body += '<hr>'
        subcstr += utils.details_block(summary, body)
        subcstr += features2html(subc)
        
        # ----#-   Subclass Subclass Spells
        spells = subc.get('subclassspells')
        if spells != None:
            summary = 'Subclass Spells'
            body = utils.convert(spells.get('description', ''))
            body += '<table class="subclass-spells">\n'
            for key in sorted(int(a) for a in spells.keys() if a.isdigit()):
                lst = spells[str(key)]
                body += '<tr>\n'
                body += '<td style="text-align: center;">%s</td>\n' % utils.ordinals[key]
                for spell in lst:
                    body += '<td>'
                    body += spellmod.spellblock(spell, spell_list)
                    body += '</td>\n'
                body += '</tr>\n'
            body += '</table>'
            subcstr += utils.details_block(summary, body)
        
        # ----#-   Subclass Spells
        spells = subc.get('spells')
        subcstr += spell_tables(spells, subc.get('max-slot', 9), spell_list)
        
        subcstr += '</div>\n'
        ret += subcstr

    # ----#-   Class Spells
    temp = spell_tables(c.get('spells'), c.get('max-slot', 9), spell_list)
    if temp:
        ret += '<div>\n%s</div>\n' % temp

    ret = spellmod.handle_spells(ret, spell_list)

    return ret
