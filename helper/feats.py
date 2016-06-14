import utils

def feat2md(feat):
    ret = ''
    
    ret += '## %s\n\n' % feat.get('name', '')
    temp = feat.get('prerequisite')
    if temp != None:
        ret += '*Prerequisite: %s*\n\n' % temp
    ret += '\n'.join(feat.get('text'))
    
    return ret

def feat2html(feat):
    ret = utils.convert(feat2md(feat))
    return ret

def featblock(feat):
    ret = ''
    ret += '<details><summary>%s</summary>\n' % str(feat['name'])
    ret += '<div class="spell-box">\n'
    ret += feat2html(feat)
    ret += '</div>\n'
    ret += '</details>'
    return ret

def main(feats, spell_list, load):
    ret = '<div>\n'
    
    temp = load('feats.md')
    if temp != None:
        ret += utils.convert(temp)

    ret += '<table id="feats-table" style="width: 100%;">\n'
    for feat in sorted(feats.keys()):
        ret += '<tr><td>\n'
        ret += featblock(feats[feat])
        ret += '</td></tr>\n'
    ret += '</table>\n'
    ret += '</div>\n'
    
    ret = utils.handle_spells(ret, spell_list)
    return ret

def boons(epicboons, spell_list, load):
    ret = '<div>\n'
    
    temp = load('epicboons.md')
    if temp != None:
        ret += utils.convert(temp)
    
    ret += '<table id="epic-boons-table" style="width: 100%;">\n'
    for boon in sorted(epicboons.keys()):
        ret += '<tr><td>\n'
        ret += featblock(epicboons[boon])
        ret += '</td></tr>\n'
    ret += '</table>\n'
    ret += '</div>\n'
    
    ret = utils.handle_spells(ret, spell_list)
    return ret
