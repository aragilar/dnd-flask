import os

from . import archiver
from . import utils
from . import spells

class MagicItem (utils.Base):
    attunement = False
    description = []
    limits = None
    rarity = 'common'
    type = 'Wondrous item'
    
    _page = None
    
    def dict(self):
        d = {
            'name': self.name,
            'attunement': self.attunement,
            'limits': self.limits,
            'rarity': self.rarity,
            'type': self.type,
        }
        return d
    
    def __str__(self):
        if self._page is None:
            ret = ''
            ret += '<h1>%s</h1>\n\n' % self.name
            
            temp = self.type
            
            if self.limits:
                temp += ' (%s)' % self.limits
            
            if isinstance(self.rarity, list):
                temp += ', rarity varies'
            else:
                temp += ', ' + self.rarity
            
            if self.attunement:
                if isinstance(self.attunement, str):
                    if self.attunement[0].upper() in 'AEIOU':
                        temp += ' (requires attunement by an %s)' % self.attunement
                    else:
                        temp += ' (requires attunement by a %s)' % self.attunement
                else:
                    temp += ' (requires attunement)'
            ret += '<p><em>%s</em></p>\n\n' % temp
            
            ret += utils.convert('\n'.join(self.description))
            
            ret = spells.handle_spells(ret, self.spell_list)
            
            ret = '<div>\n%s</div>' % ret
            
            self._page = ret
        else:
            ret = self._page
        
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
        body = str(item)
        body = body.replace('<h1>', '<h1><a href="%s">' % utils.slug(name), 1)
        body = body.replace('</h1>', '</a></h1>', 1)
        ret = utils.details_block(
            str(name),
            body,
            body_class="spell-box"
        )
    else:
        ret = str(name)
    return ret

class MagicItems (utils.Group):
    type = MagicItem
    javascript = ['magicitems.js']
    
    head = '<h1>Magic Items</h1>\n'
    
    def __init__(self, folder=None, sources=None):
        super().__init__(folder, sources)
        if folder:
            p = ''
            
            path = os.path.join(folder, 'documentation/magicitems.md')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = f.read()
                p += data
            
            path = os.path.join(folder, 'documentation/sentientitems.md')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = f.read()
                p += data
            
            path = os.path.join(folder, 'documentation/artifacts.md')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = f.read()
                p += data
            
            if p:
                p = utils.convert(p)
                p = utils.get_details(p, splttag='h1')
                p = utils.get_details(p, 'h1')
                self.head = p

    def page(self):
        itemscopy = {}
        for item in self.values():
            itemscopy[item.name] = item.dict()
        
        ret = '<script>\nitems = %s;\n</script>\n' % (archiver.p(itemscopy, compact=True))
        
        ret += spells.handle_spells(self.head, self.spell_list)
        
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
        ret += utils.details_group(temp, body_id="magicitems", body_class="spell-table")
        
        ret = '<div>\n%s</div>\n' % ret
        return ret
