import os
import re

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
            '<div>\n%s</div>\n' % str(feat),
            body_class='spell-box',
        )
    else:
        ret = str(name)
    return ret

class Feats (utils.Group):
    type = Feat
    _headfile = 'feats.md'
    head = '<h1>Feats</h1>\n'
    
    def __init__(self, folder=None, sources=None):
        super().__init__(folder, sources)
        if folder:
            folder = os.path.join(folder, 'documentation', self._headfile)
            if os.path.exists(folder):
                with open(folder, 'r') as f:
                    data = f.read()
                data = utils.convert(data)
                data = utils.get_details(data, 'h1')
                self.head = data

    def page(self):
        ret = '<div>\n'
    
        ret += self.head
        h1 = re.search('<h1>(.*?)</h1>', ret)
        if h1:
            slug = utils.slug(h1.group(1))
            ret.replace(h1.group(0), '<h1 id="%s">%s</h1>' % (slug, h1.group(1)), 1)

        temp = ''
        for feat in self:
            temp += '<tr><td>\n'
            temp += featblock(feat.name, self)
            temp += '</td></tr>\n'
        ret += utils.details_group(temp)
        
        ret += '</div>\n'
        return ret

class EpicBoons (Feats):
    type = EpicBoon
    _headfile = 'epicboons.md'
    head = '<h1>Epic Boons</h1>\n'
