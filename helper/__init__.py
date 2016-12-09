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
    singular = "Filter"
    plural = "Filters"
    tables = [{
        "table": plural,
        "fields": utils.OrderedDict([
            ("sort_index", int),
            ("name", str),
        ]),
        "constraints": {
            "sort_index": "NOT NULL UNIQUE",
            "name": "PRIMARY KEY NOT NULL",
        }
    }]

    def get_data(self, columns=["*"]):
        if self.db:
            with self.db as db:
                return db.select(
                    '%s' % self.plural,
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
        return html

class Documents (utils.Group):
    type = Document
    singular = "Document"
    plural = "Documents"
    tables = [{
        "table": plural,
        "fields": utils.OrderedDict([
            ("name", str),
            ("sort_index", int),
            ("description", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "description": "NOT NULL",
        }
    }]

    def get_data(self, columns=["*"], name=None, subtype_item=None):
        if self.db:
            conditions = ["C.sort_index is not null"]
            params = []
            if name:
                conditions.append("slug(C.name)=?")
                params.append(slug(name))
            with self.db as db:
                if name is not None:
                    self.db.conn.create_function("slug", 1, slug)
                return db.select(
                    '%s C' % self.plural,
                    columns=list(map("C.".__add__, columns)),
                    conditions=conditions,
                    order=[
                        "C.sort_index",
                        "C.name",
                    ],
                    params=params,
                )
        else:
            return []

class OptionalRules (utils.Group):
    type = Document
    singular = "Optional_Rule"
    plural = "Optional_Rules"
    tables = [{
        "table": plural,
        "fields": utils.OrderedDict([
            ("name", str),
            ("source", str),
            ("sort_index", int),
            ("description", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
            "description": "NOT NULL",
        }
    }]

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

def init(file=None):
    global database

    database = sql.DB(file)

    with database as db:
        db.curs.execute("PRAGMA journal_mode = MEMORY;")
        db.create_table(
            "sources",
            utils.OrderedDict([
                ("id", str),
                ("source_name", str),
                ("source_index", int),
                ("core", int),
            ]),
            constraints={
                "id": "PRIMARY KEY NOT NULL",
                "source_name": "NOT NULL",
                "source_index": "NOT NULL",
            },
        )
        db.commit()
        for item in l:
            for table in item.tables:
                db.create_table(**table)
                db.commit()
            if type(item) not in [Filters, Documents]:
                db.create_table(
                    item.plural + "_filters",
                    utils.OrderedDict([
                        ("filter_name", str),
                        ("item_name", str),
                    ]),
                    constraints={
                        "filter_name": "NOT NULL REFERENCES filters(id)",
                        "item_name": "NOT NULL REFERENCES %s(name)" % item.plural,
                    },
                    adtl_constraints=["PRIMARY KEY(filter_name, item_name)"],
                )
                db.commit()
            if item.subtype:
                db.create_table(
                    "sub%s_filters" % item.plural,
                    utils.OrderedDict([
                        ("filter_name", str),
                        ("item_name", str),
                    ]),
                    constraints={
                        "filter_name": "NOT NULL REFERENCES filters(id)",
                        "item_name": "NOT NULL REFERENCES sub%s(name)" % item.plural,
                    },
                    adtl_constraints=["PRIMARY KEY(filter_name, item_name)"],
                )
                db.commit()

    for item in l:
        item(database)
