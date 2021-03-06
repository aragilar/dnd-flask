import re

from . import utils
from . import spells

class Feat (utils.Base):
    def md(self):
        ret = '# %s\n\n' % self.name
        if self.prerequisite:
            ret += '*Prerequisite: %s*\n\n' % self.prerequisite
        if self.description:
            ret += self.description
        return ret

    def page(self):
        ret = self.md()
        ret = utils.convert(ret)
        ret = spells.handle_spells(ret, self.parent.get_spell_list(spells.Spells))

        return ret

def featblock(name, feats):
    feat = feats.get(name)
    if feat is not None:
        ret = utils.details_block(
            str(name),
            '<div class="spell-box">\n%s</div>\n' % feat.page(),
        )
    else:
        ret = str(name)
    return ret

class Feats (utils.Group):
    type = Feat
    singular = "Feat"
    plural = "Feats"
    tables = [{
        "table": plural,
        "fields": utils.OrderedDict([
            ("name", str),
            ("source", str),
            ("sort_index", int),
            ("prerequisite", str),
            ("description", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
            "description": "NOT NULL",
        }
    }]
    _headfile = 'feats.md'

    @property
    def head(self):
        return self.get_document("Feats", "Feats")

    def page(self):
        ret = self.head
        h1 = re.search('<h1>(.*?)</h1>', ret)
        if h1:
            slug = utils.slug(h1.group(1))
            ret = ret.replace(h1.group(0), '<h1 id="{1}">{0}</h1>'.format(h1.group(1), slug), 1)

        temp = ''
        for feat in self.values():
            temp += '<tr><td>\n'
            temp += featblock(feat.name, self)
            temp += '</td></tr>\n'
        ret += utils.details_group(temp)

        return ret

class EpicBoons (Feats):
    type = Feat
    singular = "Epic_Boon"
    plural = "Epic_Boons"
    tables = [{
        "table": plural,
        "fields": utils.OrderedDict([
            ("name", str),
            ("source", str),
            ("sort_index", int),
            ("prerequisite", str),
            ("description", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
            "description": "NOT NULL",
        }
    }]
    _headfile = 'epicboons.md'

    @property
    def head(self):
        return self.get_document("Epic Boons", "Epic Boons")
