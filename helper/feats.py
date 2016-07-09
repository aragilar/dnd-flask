from . import utils
from . import spells

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
    summary = str(feat['name'])
    body = '<div>\n%s</div>' % feat2html(feat)
    return utils.details_block(summary, body, body_class='spell-box')

def main(feats, spell_list, load, t='feats'):
    ret = '<div>\n'
    
    temp = load('%s.md' % t.replace('-', ''))
    if temp != None:
        ret += utils.convert(temp)

    temp = '<table id="%s-table" style="width: 100%%;">\n' % t
    for feat in sorted(feats.keys()):
        temp += '<tr><td>\n'
        temp += featblock(feats[feat])
        temp += '</td></tr>\n'
    temp += '</table>\n'
    ret += utils.details_group(temp)
    ret += '</div>\n'
    
    ret = spells.handle_spells(ret, spell_list)
    return ret

def boons(epicboons, spell_list, load):
    return main(epicboons, spell_list, load, 'epic-boons')
