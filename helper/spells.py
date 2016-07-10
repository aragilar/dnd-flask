import re
from . import archiver
from . import utils

spellexpression = re.compile('''(?<!<p>)(
<spell>
(.*?)
</spell>
)(?!</p>)''', re.X)

spellexpression_p = re.compile('''(
<p>
<spell>
(.*?)
</spell>
</p>
)''', re.X)

def spells_by_class(classes):
    new = {}
    for c in classes.keys():
        d = []
        
        cdict = classes[c]
        slist = cdict.get('spells', {})
        
        #for x in ['Cantrip'] + map(str, range(1, 10)):
        for x in slist.keys():
            d.extend(slist.get(x, []))
        d.sort()
        if len(d):
            new[c] = d
    return new

def handle_spells(text, spells):
    spelllist = list(spellexpression_p.finditer(text))
    spelllist += list(spellexpression.finditer(text))
    spelllist = map(lambda a: a.groups(), spelllist)
    for item in spelllist:
        text = text.replace(item[0], utils.details_group(spellblock(item[-1], spells)))
    return text

def spellblock(spellname, spells):
    spell = spells.get(spellname, {'name': spellname})
    if spell != None:
        ret = utils.details_block(
            str(spellname),
            '<div>\n%s</div>' % spell2html(spell),
            body_class="spell-box"
        )
    else:
        ret = str(spellname)
    return ret

def spell2html(spell):
    ret = '<h2>%s</h2>\n' % spell['name']
    
    lvl = spell.get('level', '0')
    
    type = spell.get('type', 'Unknown Type')
    
    if lvl == 'Cantrip':
        lvl = '%s Cantrip' % type
    else:
        lvl = '%s-level %s' % (utils.ordinals[int(lvl)], type)
    
    if spell.get('ritual', False):
        lvl += ' (ritual)'
    
    ret += '<p>\n<em>%s</em><br>\n' % lvl
    
    ret += '<strong>Casting Time:</strong> %s<br>\n' % spell.get('cast time', 'Unknown Casting Time')
    ret += '<strong>Range:</strong> %s<br>\n' % spell.get('range', 'Unknown Range')
    
    components = spell.get('components', {})
    
    lst = []
    truncated = True
    
    if components.get('verbal', False):
        lst.append('Verbal')
        if truncated:
            lst[-1] = lst[-1][0]
    if components.get('somatic', False):
        lst.append('Somatic')
        if truncated:
            lst[-1] = lst[-1][0]
    if components.get('material', ''):
        lst.append('Material')
        if truncated:
            lst[-1] = lst[-1][0]
        lst[-1] += ' (%s)' % components.get('material', 'Unknown Material Component')
    
    if len(lst) == 0:
        lst.append('None')
    
    ret += '<strong>Components:</strong> %s<br>\n' % ', '.join(lst)
    ret += '<strong>Duration:</strong> %s\n</p>\n' % spell.get('duration', 'Unknown Duration')
    
    lst = spell.get('description', [])
    
##    for x in range(len(lst)):
##        item = lst[x]
##        lst[x] = item
    
    ret += utils.convert('\n'.join(lst))
    return ret

def main(spells, classes, load, compact = True):
    ret = '<div>\n'
    byClass = spells_by_class(classes)
    spellscopy = {}
    for spell in spells.keys():
        temp = spells[spell].copy()
        del temp['description']
        spellscopy[spell] = temp
    
    ret += '<script>\nspells = %s;\n\nclasses = %s\n</script>\n' % (archiver.p(spellscopy, compact = compact), archiver.p(byClass, compact = compact))
    
    temp = load('spellcasting.md')
    if temp:
        ret += utils.get_details(utils.get_details(utils.convert(temp)), 'h1')
    else:
        ret += '<h1>Spells</h1>\n'
    ret += '<div style="padding: 5px; margin: 5px auto;">\n'
    
    for c in sorted(byClass.keys()):
        ret += '\t<label style="clear: right; float: right; padding: 2px;">%s: <input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="%s"></label>\n' % (c, c)
    
    ret += '''<h2>Search</h2>
    Name: <input style="padding: inherit; margin: inherit;" class="filter" id="name"><br>
    Level: <input style="padding: inherit; margin: inherit;" class="filter" id="level"><br>
    School: <input style="padding: inherit; margin: inherit;" class="filter" id="type"><br>
    <label>Ritual: <input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="ritual"></label><br>
    
    <!--Nonverbal: <input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="nonverbal"><br>
    Nonsomatic: <input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="nonsomatic"><br>
    Immaterial: <input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="immaterial"><br>-->
    <span style="margin: 5px; display: block; clear: both;">Count: <output id="count">0</output></span>
</div>'''

    temp = '<table id="spells" class="spell-table">\n<tr><td>\n'
    temp += '</td></tr>\n<tr><td>\n'.join(utils.asyncmap(
            lambda a: spellblock(a, spells),
            list(sorted(spells.keys()))
    ))
    temp += '</td></tr>\n</table>\n'
    ret += utils.details_group(temp, body_class="spell-table")
    ret += '</div>\n'
    #ret = load.html_back(top + ret, 'Spells', 'spells/', ['../items.css'], ['spells.js'])
    return ret
