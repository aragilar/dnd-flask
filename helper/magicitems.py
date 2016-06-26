import archiver
import utils

def item2md(item):
    ret = ''
    ret += '# %s\n\n' % item.get('name', '')
    temp = item.get('type', '')
    limit = item.get('limits')
    if limit:
        temp += ' (%s)' % limit
    _ = item.get('rarity', '')
    if isinstance(_, list):
        temp += ', rarity varies'
    else:
        temp += ', ' + _
    attunement = item.get('attunement')
    if attunement:
        if isinstance(attunement, basestring):
            if attunement[0].lower() in 'aeiou':
                temp += ' (requires attunement by an %s)' % attunement
            else:
                temp += ' (requires attunement by a %s)' % attunement
        else:
            temp += ' (requires attunement)'
    ret += '*%s*\n\n' % temp
    
    ret += '\n'.join(item.get('description', []))
    return ret

def item2html(item):
    ret = utils.convert(item2md(item))
    return ret

def itemblock(item):
    ret = '<details class="spell-box"><summary>%s</summary>\n' % str(item.get('name'))
    ret += '<div>\n'
    ret += item2html(item)
    ret += '</div>\n'
    ret += '</details>'
    return ret

def main(items, spell_list, load, compact = True):
    itemscopy = {}
    for key in items:
        item = {}
        item.update(items[key])
        del item['description']
        itemscopy[key] = item
    
    ret = '<script>\nitems = %s;\n</script>\n' % (archiver.p(itemscopy, compact = compact))
    
    head = ''
    for item in ['magicitems.md', 'sentientitems.md', 'artifacts.md']:
        temp = load(item)
        if temp != None:
            temp = temp.strip('\n')
            if temp:
                head += utils.get_details(utils.get_details(utils.convert(temp)), 'h1')
    if not head:
        head = '<h1>Magic Items</h1>\n'
    ret += head
    
    ret += '''<div style="padding: 5px; margin: 5px auto;">
    
    <h2>Search</h2>
    
    Name: <input style="padding: inherit; margin: inherit;" class="filter" id="name"><br>
    <br>
    <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="attuned" checked> Attuned</label><br>
    <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="unattuned" checked> Unattuned</label><br>
    
    <br>
    
    <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="common"> Common</label><br>
    <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="uncommon"> Uncommon</label><br>
    <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="rare"> Rare</label><br>
    <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="very_rare"> Very Rare</label><br>
    <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="legendary"> Legendary</label><br>
    
    <!--<label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="unique"> Unique</label><br>-->
    <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="sentient"> Sentient</label><br>
    <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="artifact"> Artifacts</label><br>
    
    <span style="margin: 5px; display: block; clear: both;">Count: <output id="count">0</output></span>
</div>'''

    ret += '<table id="magicitems" class="spell-table" style="width: 100%;">\n'
    for item in sorted(items.keys()):
        ret += '<tr><td>%s</td></tr>\n' % itemblock(items[item])
    ret += '</table>\n'
    
    ret = utils.handle_spells(ret, spell_list)
    
    ret = '<div>\n%s\n</div>' % ret
    return ret
