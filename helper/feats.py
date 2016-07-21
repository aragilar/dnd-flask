from . import utils
from . import spells

class Feat (utils.Base):
    prerequisite = None
    text = []
    
    def __str__(self):
        ret = '<h2>%s</h2>\n\n' % self.name
        if self.prerequisite is not None:
            ret += '<em>Prerequisite: %s</em>\n\n' % self.prerequisite
        ret += utils.convert('\n'.join(self.text))
        
        ret = spells.handle_spells(ret, self.spell_list)
        
        return ret

class EpicBoon (Feat):
    pass

def featblock(name, feats):
    feat = feats.get(name)
    if feat is not None:
        ret = utils.details_block(
            str(name),
            '<div>\n%s</div>' % str(feat),
            body_class='spell-box',
        )
    else:
        ret = str(name)
    return ret

class Feats (utils.Group):
    type = Feat

    def page(self, load, t='feats'):
        ret = '<div>\n'
    
        temp = load('%s.md' % t.replace('-', ''))
        if temp != None:
            ret += utils.convert(temp)
        ret = ret.replace('<h1>', '<h1 id="%s">' % t)

        temp = ''
        for feat in self:
            temp += '<tr><td>\n'
            temp += featblock(feat.name, self)
            temp += '</td></tr>\n'
        ret += utils.details_group(temp)#, body_class='%s-table'%t)
        
        ret += '</div>\n'
        return ret

class EpicBoons (Feats):
    type = EpicBoon

    def page(self, load):
        return Feats.page(self, load, t='epic-boons')
