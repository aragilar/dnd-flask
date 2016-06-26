import math
import re
import utils

def spell_tables(spells, maxslot, spell_list):
    table_style = 'class="spell-table"'
    head_row_style = 'class="head-row"'
    ret = ''
    if spells != None:
        cantrips = spells.get('Cantrip', [])
        if len(cantrips):
            ret += '<details><summary>Cantrips</summary>\n'
            ret += '<table %s>\n' % table_style
            ret += '<tr><th %s>Cantrips</th></tr>' % head_row_style
            for item in cantrips:
                if item in spell_list:
                    temp = utils.spellblock(item, spell_list)
                    ret += '<tr><td>\n%s\n</td></tr>\n' % temp
            ret += '</table>\n'
            ret += '</details>\n'

        if len(spells.get('1', [])) and maxslot > 0:
            ret += '<details><summary>Spells</summary>\n'
            ret += '<table %s>\n' % table_style
            for x in xrange(1, maxslot + 1):
                if str(x) in spells:
                    lst = spells[str(x)]
                else:
                    lst = []

                if len(lst):
                    ret += '<tr><th %s>%s-Level Spells</th></tr>\n' % (head_row_style, utils.ordinals[x])
                    for item in lst:
                        if item in spell_list:
                            temp = utils.spellblock(item, spell_list)
                            ret += '<tr><td>\n%s\n</td></tr>\n' % temp
            ret += '</table>\n'
            ret += '</details>\n'
    return ret

def features2html(c):
    lst = c.get('features', [[]])
    data = c.get('features-data', {})
    ret = ''
    
    # ----#-   Table
    table = c.get('table')
    magic = c.get('magic', 0)
    if table != None or magic > 0:
        if table == None:
            table = {}
        
        if magic > 0: # figure out the level of the maximum spell slot
            if c.has_key('max-slot'):
                x = c['max-slot']
            else:
                y = c.get('max-level', 20)
                if y < magic:
                    y = 0
                else:
                    y = int(math.ceil(y / float(magic)))
                for x in xrange(len(utils.spellslots[-1])):
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
            headrows += map(lambda a: utils.ordinals[a] + '-Level', xrange(1, x + 1))
        
        ret += '<details><summary>Table</summary>\n'
        ret += '<table>\n'
        
        if magic:
            ret += '<caption>%sSpell Slots</caption>\n' % ('&nbsp;' * len(headrows) * 3)
        
        emptycolstyle = ' style="min-width: 0px;"'
        ret += '<tr>\n'
        for item in headrows:
            style = ''
            if item == '':
                style = emptycolstyle
            ret += '<th%s>%s</th>\n' % (style, item)
        ret += '</tr>\n'
        
        for x in xrange(1, c.get("max-level", 20)+1):
            ret += '<tr>\n'
            for item in headrows:
                if item != '':
                    ret += '<td style="text-align: center;">'
                    if item == 'Level': # character level
                        ret += utils.ordinals[x]
                    elif item in table: # data specific to the class
                        ret += str(table.get(item, [])[x-1])
                    elif item[:3] in utils.ordinals: # spell slots
                        if x < magic:
                            y = 0
                        else:
                            y = int(math.ceil(x / float(magic)))
                        z = utils.ordinals.index(item[:3]) - 1
                        ret += str(utils.spellslots[y][z])
                    ret += '</td>\n'
                else:
                    ret += '<td%s></td>\n' % emptycolstyle
            ret += '</tr>\n'
        ret += '</table>\n'
        ret += '</details>\n\n'
    
    # ----#-   Features
    ret += '<ol>\n'
    for x, line in enumerate(lst):
        if len(line) and x > 0:
            format = '<li value="%d">%%s</li>\n' % x
        else:
            format = '%s'
        
        linestr = ''
        for item in line:
            linestr += '<details><summary>%s</summary>\n' % item
            temp = data.get(item, [])
            temp = '\n'.join(temp)
            
            temp = utils.convert(temp)
            temp = utils.get_details(temp)
            temp = re.sub('<h2.*?>', '', temp)
            temp = temp.replace('</h2>', '')
            
            linestr += temp
            linestr += '</details>\n'
        
        format = format % linestr
        ret += format
    ret += '</ol>\n'
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

def class2html(c, spell_list, release_sort=sorted):
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
    ret += '<details><summary><h2>Features</h2></summary>\n\n'
    
    short = '**Description:** %s  \n' % c.get('description', '')
    short += '**Hit Die:** %s  \n' % c.get('hit die', '')
    temp = c.get('primary stat', [])
    sep = 'and'
    if temp[-1] == '/':
        sep = 'or'
        temp = temp[:-1]
    temp = map(lambda a: utils.stats[a], temp)
    if len(temp) > 1:
        short += '**Primary Abilities:** %s  \n' % utils.comma_list(temp, sep)
    elif len(temp) == 1:
        short += '**Primary Ability:** %s  \n' % temp[0]
    temp = c.get('saving throws', [])
    temp = map(lambda a: utils.stats[a], temp)
    if len(temp) > 1:
        short += '**Saving Throw Proficiencies:** %s  \n' % utils.comma_list(temp)
    elif len(temp) == 1:
        short += '**Saving Throw Proficiency:** %s  \n' % temp[0]
    short += '**Armor and Weapon Proficiencies:** %s  \n' % utils.comma_list(c.get('combat proficiencies', []))
    temp = utils.choice_list(c.get('tool proficiencies', []))
    if temp != 'none':
        short += '**Tool Proficiencies:** %s  \n' % temp
    short += '**Skills:** %s\n\n' % utils.choice_list(c.get('skills', []))
    temp = c.get('equipment', [])
    if len(temp):
        short += '**Equipment**  \n'
        short += 'You start with the following equipment in addition to the equipment granted by your background:\n\n'
        for item in temp:
            short += '* %s\n' % equipment_row(item)
    ret += utils.convert(short)
    
    ret += '</details>\n'

    # ----#-   Class Features
    ret += features2html(c)

    # ----#-   Class Foot
    temp = c.get('foot', [])
    for item in temp:
        if len(item) > 1:
            ret += '<details><summary>%s</summary>\n' % item[0]
            temp = utils.convert('\n'.join(item[1:]))
            temp = utils.get_details(temp)
            ret += temp
            ret += '</details>\n'
    ret += '</div>\n'

    # ----#-   Subclass
    subclassdict = c.get('subclass', {})
    for name in release_sort(subclassdict):
        subc = subclassdict.get(name, {})
        subcstr = '\n<div>\n\n'
        
        # ----#-   Subclass Features
        subcstr += '<details><summary>%s</h2></summary>\n' % utils.convert('## ' + subc.get('name', ''))
        subcstr += utils.convert('\n'.join(subc.get('description', '')))
        subcstr += '</details>\n'
        subcstr += features2html(subc)
        
        # ----#-   Subclass Foot
        temp = subc.get('foot', [])
        for item in temp:
            if len(item) > 1:
                subcstr += '<details><summary>%s</summary>\n' % item[0]
                temp = utils.convert('\n'.join(item[1:]))
                subcstr += temp
                subcstr += '</details>\n'
        
        # ----#-   Subclass Subclass Spells
        spells = subc.get('subclassspells')
        if spells != None:
            subcstr += '\n<details><summary>Subclass Spells</summary>\n'
            subcstr += utils.convert(spells.get('description', ''))
            subcstr += '<table>\n'
            for key in sorted(filter(lambda a: a.isdigit(), spells.keys()), key = lambda a: int(a)):
                lst = spells[key]
                subcstr += '<tr>\n'
                subcstr += '<td style="text-align: center;">%s</td>\n' % utils.ordinals[int(key)]
                for spell in lst:
                    subcstr += '<td>'
                    subcstr += utils.spellblock(spell, spell_list)
                    subcstr += '</td>\n'
                subcstr += '</tr>\n'
            subcstr += '</table>\n'
            subcstr += '</details>\n'
        
        # ----#-   Subclass Spells
        spells = subc.get('spells')
        subcstr += spell_tables(spells, subc.get('max-slot', 9), spell_list)
        
        subcstr += '</div>'
        ret += subcstr

    # ----#-   Class Spells
    if c.get('spells') != None:
        ret += '\n<div>\n'
        spells = c.get('spells')
        ret += spell_tables(spells, c.get('max-slot', 9), spell_list)
        ret += '</div>'

    ret = utils.handle_spells(ret, spell_list)

    return ret
