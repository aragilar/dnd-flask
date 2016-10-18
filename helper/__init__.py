import sys
import os
import re
import collections

from . import sql
from . import utils
from . import classes
from . import races
from . import backgrounds
from . import spells
from . import feats
from . import monsters
from . import magicitems
from . import items

slug = utils.slug

class Filters (utils.Group):
    tablename = "filters"
    
    def get_data(self, columns=["*"]):
        if self.db:
            with self.db as db:
                return db.select(
                    '%s' % self.tablename,
                    columns=columns,
                    order=[
                        "sort_index",
                        "name",
                    ],
                )
        else:
            return []

class Document (utils.Base):
    def __init__(self, parent, d):
        if d["description"] is None:
            d["description"] = ""
        super().__init__(parent, d)

    def page(self):
        html = "<h1>%s</h1>\n\n" % self.name
        html += utils.convert(self.description)
        html = '<div>\n%s</div>\n' % html
        return html

class Documents (utils.Group):
    type = Document
    tablename = "documents"

    def get_data(self, columns=["*"]):
        if self.db:
            with self.db as db:
                return db.select(
                    '%s C' % self.tablename,
                    columns=list(map("C.".__add__, columns)),
                    conditions=["C.sort_index is not null"],
                    order=[
                        "C.sort_index",
                        "C.name",
                    ],
                )
        else:
            return []

class OptionalRules (utils.Group):
    type = Document
    tablename = "optional_rules"

database = None
filter_list = Filters()
class_list = classes.Classes()
race_list = races.Races()
document_list = Documents()
background_list = backgrounds.Backgrounds()
spell_list = spells.Spells()
feat_list = feats.Feats()
epicboon_list = feats.EpicBoons()
monster_list = monsters.Monsters()
magicitem_list = magicitems.MagicItems()
weapon_list = items.Weapons()
armor_list = items.Armors()
optionalrule_list = OptionalRules()
item_list = items.Items()

def init(file=None):
    global database

    l = [
        filter_list,
        class_list,
        race_list,
        document_list,
        background_list,
        spell_list,
        feat_list,
        epicboon_list,
        monster_list,
        magicitem_list,
        weapon_list,
        armor_list,
        optionalrule_list,
        item_list,
    ]

    database = sql.DB(file)

    for item in l:
        item(database)
