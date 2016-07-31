import os

from . import archiver
from . import utils
from . import spells

class Monster (utils.Base):
    description = []
    
    _page = None
    
    def dict(self):
        d = {
            'name': self.name,
        }
        return d
    
    def __str__(self):
        if self._page is None:
            ret = ''
            ret = spells.handle_spells(ret, self.spell_list)
            
            self._page = ret
        else:
            ret = self._page
        
        return ret

def monsterblock(name, monsters=None):
    if name is None:
        name = ''
        monster = None
    elif monsters is None:
        monster = name
        name = monster.name
    else:
        monster = monsters.get(name)
    if monster is not None:
        ret = '<li><a href="{0}">{0}</a></li>\n'.format(name)
    else:
        ret = str(name)
    return ret

class Monsters (utils.Group):
    type = Monster
    javascript = ['monsters.js']
    
    head = '<h1>Monsters</h1>\n'
    
    def __init__(self, folder=None, sources=None):
        super().__init__(folder, sources)
        self.groups = {}
        if folder:
            path = os.path.join(folder, 'documentation/monsters.md')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = f.read()
                data = utils.convert(data)
                data = utils.get_details(data, splttag='h1')
                data = utils.get_details(data, 'h1')
                self.head = data

    def page(self):
        itemscopy = {}
        for item in self.values():
            itemscopy[item.name] = item.dict()
        
        ret = '<script>\nmonsters = %s;\n</script>\n' % (archiver.p(itemscopy, compact=True))
        
        ret += self.head
        
        ret += '''
        <div style="padding: 5px; margin: 5px auto;">
        
        <h2>Search</h2>
        
        </div>
        '''

        temp = ''.join(utils.asyncmap(
            monsterblock,
            self.values(),
        ))
        ret += utils.details_group(temp, body_id="monsters", body_class="spell-table")
        
        ret = '<div>\n%s</div>\n' % ret
        return ret
