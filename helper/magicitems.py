import json

from . import utils
from . import spells

class MagicItem (utils.Base):
    def __init__(self, parent, d):
        for key, value in {
            "rarity": "common",
            "category": "Wondrous item",
        }.items():
            if d[key] is None:
                d[key] = value

        if d["attunement"] == '0':
            d["attunement"] = False
        elif d["attunement"] == '1':
            d["attunement"] = True

        super().__init__(parent, d)

    def dict(self):
        d = {
            'name': self.name,
            'attunement': self.attunement,
            'limits': self.limits,
            'rarity': self.rarity,
            'type': self.category,
        }
        return d

    def md(self):
        ret = '# %s\n\n' % self.name

        temp = self.category

        if self.limits:
            temp += ' (%s)' % self.limits

        if isinstance(self.rarity, list):
            rarity = self.rarity.copy()
        else:
            rarity = [self.rarity]

        if 'sentient' in rarity:
            rarity.remove('sentient')

        if len(rarity) == 1:
            temp += ', ' + rarity[0]
        else:
            temp += ', rarity varies'

        if self.attunement:
            if isinstance(self.attunement, str):
                if self.attunement[0].upper() in 'AEIOU':
                    temp += ' (requires attunement by an %s)' % self.attunement
                else:
                    temp += ' (requires attunement by a %s)' % self.attunement
            else:
                temp += ' (requires attunement)'
        ret += '*%s*\n\n' % temp

        ret += self.description

        return ret

    def page(self):
        ret = self.md()
        ret = utils.convert(ret)
        ret = spells.handle_spells(ret,
            self.parent.get_spell_list(spells.Spells))
        return ret

def itemblock(name, magicitems=None):
    if name is None:
        name = ''
        item = None
    elif magicitems is None:
        item = name
        name = item.name
    else:
        item = magicitems.get(name)
    if item is not None:
        ret = '<li><a href="/magicitems/{1}">{0}</a></li>\n'.format(name, utils.slug(name))
    else:
        ret = str(name)
    return ret

class MagicItems (utils.Group):
    type = MagicItem
    singular = "Magic_Item"
    plural = "Magic_Items"
    tables = [{
        "table": plural,
        "fields": utils.OrderedDict([
            ("name", str),
            ("source", str),
            ("sort_index", int),
            ("rarity", str),
            ("category", str),
            ("limits", str),
            ("attunement", str),
            ("description", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
            "rarity": "NOT NULL",
            "category": "NOT NULL",
            "description": "NOT NULL",
        }
    }]
    javascript = ['magicitems.js']

    @property
    def head(self):
        header = self.get_document("Magic Items", "Magic Items")
        header2 = self.get_document("Sentient Items")
        header3 = self.get_document("Artifacts")
        if header2:
            header += header2
        if header3:
            header += header3
        return header

    def page(self):
        itemscopy = {}
        for item in self.values():
            itemscopy[item.name] = item.dict()

        ret = '<script>\nitems = %s;\n</script>\n' % (json.dumps(itemscopy))

        ret += spells.handle_spells(self.head, self.get_spell_list(spells.Spells))

        ret += '''
        <div class="search-box clearfix">
        <h2>Search</h2>
        <div class="pull-right">
            <p><label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="common"> Common</label></p>
            <p><label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="uncommon"> Uncommon</label></p>
            <p><label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="rare"> Rare</label></p>
            <p><label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="very_rare"> Very Rare</label></p>
            <p><label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="legendary"> Legendary</label></p>
            <p><label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="artifact"> Artifacts</label></p>
        </div>
        <p>Name: <input style="padding: inherit; margin: inherit;" class="filter" id="name"></p>
        <br>
        <p><label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="attuned" checked> Attuned</label><p>
        <p><label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="unattuned" checked> Unattuned</label><p>
        <br>
        <p>Count: <output id="count">0</output></p>
        </div>
        '''

        temp = ''.join(utils.asyncmap(
                itemblock,
                self.values(),
        ))
        ret += '<ul id="magicitems" class="link-list">\n%s</ul>\n' % temp

        return ret
