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
        ret = utils.details_block(
            name,
            '<div>\n%s</div>' % str(item),
            body_class="spell-box"
        )
    else:
        ret = str(name)
    return ret

class MagicItems (utils.Group):
    type = MagicItem
    javascript = ['magicitems.js']
    
    head = '# Magic Items'
    sentients = ''
    artifacts = ''
    
    def __init__(self, folder=None, sources=None):
        super().__init__(folder, sources)
        if folder:
            path = os.path.join(folder, 'documentation/magicitems.md')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = f.read()
                self.head = data
            
            path = os.path.join(folder, 'documentation/sentientitems.md')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = f.read()
                self.sentients = data
            
            path = os.path.join(folder, 'documentation/artifacts.md')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = f.read()
                self.artifacts = data

    def page(self):
        itemscopy = {}
        for item in self.values():
            itemscopy[item.name] = item.dict()
        
        ret = '<script>\nitems = %s;\n</script>\n' % (archiver.p(itemscopy, compact=True))
        
        head = ''
        for item in [self.head, self.sentients, self.artifacts]:
            if item:
                temp = utils.convert(item)
                temp = utils.get_details(temp)
                head += temp
        
        ret += utils.get_details(head, 'h1')
        
        ret += '''
        <div style="padding: 5px; margin: 5px auto;">
        
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
        </div>
        '''

        temp = ''.join(utils.asyncmap(
                itemblock,
                self.values(),
        ))
        ret += utils.details_group(temp, body_id="magicitems", body_class="spell-table")
        
        ret = '<div>\n%s</div>\n' % ret
        return ret
