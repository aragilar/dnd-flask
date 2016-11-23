import os
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

    def page(self):
        ret = ''
        ret += '<h1>%s</h1>\n\n' % self.name

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
        ret += '<p><em>%s</em></p>\n\n' % temp

        ret += utils.convert(self.description)

        ret = spells.handle_spells(ret, self.parent.get_spell_list(spells.Spells))

        ret = '<div>\n%s</div>' % ret

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
    tablename = "magic_items"
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

        ret = '<script>\nitems = %s;\n</script>\n' % (json.dumps(itemscopy, sort_keys=True))

        ret += spells.handle_spells(self.head, self.get_spell_list(spells.Spells))

        ret += '''
        <div class="search-box">
        <h2>Search</h2>
        <p>Name: <input style="padding: inherit; margin: inherit;" class="filter" id="name"></p>
        <p class="right">
            <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="common"> Common</label>
            <br>
            <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="uncommon"> Uncommon</label>
            <br>
            <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="rare"> Rare</label>
            <br>
            <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="very_rare"> Very Rare</label>
            <br>
            <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="legendary"> Legendary</label>
            <br>
            <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter rarity" id="artifact"> Artifacts</label>
        </p>
        <p>
            <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="attuned" checked> Attuned</label>
            <br>
            <label><input style="padding: inherit; margin: inherit;" type="checkbox" class="filter" id="unattuned" checked> Unattuned</label>
        <p>
        <p>Count: <output id="count">0</output></p>
        </div>
        '''

        temp = ''.join(utils.asyncmap(
                itemblock,
                self.values(),
        ))
        ret += '<ul id="magicitems" class="spell-table">\n%s</ul>\n' % temp

        ret = '<section>\n%s</section>\n' % ret
        return ret
