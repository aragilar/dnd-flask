from . import utils

class Weapon (utils.Base):
    def __init__(self, parent, d):
        for key, value in {
            "cost": 0.0,
            "damage": "",
            "damage_type": "unknown",
            "weight": "0",
            "properties": "-",
            "type": "other",
            "special": None,
        }.items():
            if d[key] is None:
                d[key] = value

        d["ranged"] = bool(d["ranged"])

        super().__init__(parent, d)

    def page(self):
        ret = '<tr>\n'

        ret += '<td>%s</td>\n' % self.name

        if self.cost > 0:
            if self.cost < 0.1:
                ret += '<td>%d cp</td>\n' % int(self.cost * 100)
            elif self.cost < 1:
                ret += '<td>%d sp</td>\n' % int(self.cost * 10)
            else:
                ret += '<td>%d gp</td>\n' % int(self.cost)
        else:
            ret += '<td>-</td>\n'

        if not self.damage:
            self.damage = "-"
        if not self.damage_type:
            self.damage_type = "-"
        ret += '<td>%s %s</td>' % (self.damage, self.damage_type)
        ret += '<td>%s lb.</td>\n' % self.weight
        ret += '<td>%s</td>\n' % ', '.join(self.properties)

        ret += '</tr>\n'
        return ret

class Weapons (utils.Group):
    type = Weapon
    singular = "Weapon"
    plural = "Weapons"
    tables = [{
        "table": plural,
        "fields": utils.OrderedDict([
            ("name", str),
            ("source", str),
            ("sort_index", int),
            ("cost", float),
            ("damage", str),
            ("damage_type", str),
            ("weight", str),
            ("properties", str),
            ("type", str),
            ("ranged", int),
            ("special", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
        }
    }]

    @property
    def head(self):
        with self.db as db:
            text = db.select('documents', conditions="name=='Weapons'")
        if text:
            text = text[0]
            title = "# %s\n\n" % text['name']
            body = text['description']
            text = title + body
        else:
            text = '# Weapons\n\n'
        return text

    def page(self):
        temp = ''

        temp += self.head
        temp += '\n\n'

        temp += '## Special\n\n'
        for item in self.values():
            if item.special:
                temp += '**%s** %s\n\n' % (item.name, item.special)
        temp = utils.get_details(utils.convert(temp))

        temp += '<table id="weapons-table">\n'
        temp += '<tr><th>Name</th><th>Cost</th><th>Damage</th><th>Weight</th><th>Properties</th></tr>'
        martial_melee = []
        martial_ranged = []
        simple_melee = []
        simple_ranged = []
        other = []
        for weapon in self.values():
            if weapon.type == 'martial':
                if not weapon.ranged:
                    martial_melee.append(weapon)
                else:
                    martial_ranged.append(weapon)
            elif weapon.type == 'simple':
                if not weapon.ranged:
                    simple_melee.append(weapon)
                else:
                    simple_ranged.append(weapon)
            else:
                other.append(weapon)

        for name, lst in [('Simple Melee', simple_melee), ('Simple Ranged', simple_ranged), ('Martial Melee', martial_melee), ('Martial Ranged', martial_ranged), ('Other', other)]:
            if lst:
                temp += '<tr><th colspan="5">%s</th></tr>\n' % name
                for weapon in lst:
                    temp += weapon.page()

        temp += '</table>\n'
        temp = utils.get_details(temp, 'h1')

        return temp

class Armor (utils.Base):
    def __init__(self, parent, d):
        for key, value in {
            "type": "other",
            "ac": "-",
            "cost": 0.0,
            "strength": 0,
            "weight": "0",
        }.items():
            if d[key] is None:
                d[key] = value

        d["stealth"] = bool(d["stealth"])

        super().__init__(parent, d)

    def page(self):
        ret = '<tr>\n'

        ret += '<td>%s</td>' % self.name

        if self.cost > 0:
            if self.cost < 0.1:
                ret += '<td>%d cp</td>\n' % int(self.cost * 100)
            elif self.cost < 1:
                ret += '<td>%d sp</td>\n' % int(self.cost * 10)
            else:
                ret += '<td>%d gp</td>\n' % int(self.cost)
        else:
            ret += '<td>-</td>\n'

        ret += '<td>%s</td>\n' % self.ac

        if self.strength:
            ret += '<td>%d</td>\n' % self.strength
        else:
            ret += '<td>-</td>\n'

        if self.stealth:
            ret += '<td>Disadvantage</td>\n'
        else:
            ret += '<td>-</td>\n'

        ret += '<td>%s</td>\n' % self.weight

        ret += '</tr>\n'
        return ret

class Armors (utils.Group):
    type = Armor
    singular = "Armor"
    plural = "Armors"
    tables = [{
        "table": plural,
        "fields": utils.OrderedDict([
            ("name", str),
            ("source", str),
            ("sort_index", int),
            ("type", str),
            ("ac", str),
            ("cost", float),
            ("strength", int),
            ("stealth", int),
            ("weight", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
            "ac": "NOT NULL",
        }
    }]

    @property
    def head(self):
        with self.db as db:
            text = db.select('documents', conditions="name=='Armor and Shields'")
        if text:
            text = text[0]
            title = "# %s\n\n" % text['name']
            body = text['description']
            text = title + body
        else:
            text = '# Armor and Shields\n\n'
        return text

    def page(self):
        temp = ''

        temp += self.head
        temp += '\n\n'

        temp = utils.get_details(utils.convert(temp))

        temp += '<table id="armor-table">\n'
        temp += '<tr><th>Armor</th><th>Cost</th><th>Armor Class (ac)</th><th>Strength</th><th>Stealth</th><th>Weight</th></tr>'
        light = []
        medium = []
        heavy = []
        other = []
        alist = self.values()
        alist = sorted(alist, key=lambda a: not a.stealth)
        alist = sorted(alist, key=lambda a: a.ac)
        alist = sorted(alist, key=lambda a: a.cost if a.cost else float('inf'))
        for armor in alist:
            type = armor.type
            if type == 'light':
                light.append(armor)
            elif type == 'medium':
                medium.append(armor)
            elif type == 'heavy':
                heavy.append(armor)
            else:
                other.append(armor)

        for name, lst in [('Light', light), ('Medium', medium), ('Heavy', heavy), ('Other', other)]:
            if lst:
                temp += '<tr><th colspan="6">%s</th></tr>\n' % name
                for armor in lst:
                    temp += armor.page()
        temp += '</table>\n'
        temp = utils.get_details(temp, 'h1')

        return temp

class Item (utils.Base):
    def __init__(self, parent, d):
        for key, value in {
            "cost": 0.0,
            "weight": "-",
            "description": "",
        }.items():
            if d[key] is None:
                d[key] = value

        super().__init__(parent, d)

    def page(self):
        temp = self.description
        if temp:
            temp = utils.convert(str(temp))

        ret = '<td>'
        ret += utils.details_group(utils.details_block(self.name, temp))
        ret += '</td>\n'

        if isinstance(self.cost, str):
            ret += '<td>-</td>\n'
        elif self.cost > 0:
            if self.cost < 0.1:
                ret += '<td>%d cp</td>\n' % int(self.cost * 100)
            elif self.cost < 1:
                ret += '<td>%d sp</td>\n' % int(self.cost * 10)
            else:
                ret += '<td>%d gp</td>\n' % int(self.cost)
        else:
            ret += '<td>-</td>\n'

        ret += '<td>%s</td>\n' % self.weight

        ret = '<tr>%s</tr>\n' % ret

        return ret

class Items (utils.Group):
    type = Item
    singular = "Item"
    plural = "Items"
    tables = [
    {
        "table": "item_groups",
        "fields": utils.OrderedDict([
            ("name", str),
            ("description", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
            "description": "NOT NULL",
        }
    },
    {
        "table": plural,
        "fields": utils.OrderedDict([
            ("name", str),
            ("source", str),
            ("sort_index", int),
            ("item_group", str),
            ("cost", float),
            ("weight", str),
            ("description", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
            "item_group": "REFERENCES item_groups(name)",
        }
    }
    ]

    @property
    def head(self):
        with self.db as db:
            text = db.select('documents', conditions="name=='Items'")
        if text:
            text = text[0]
            title = "# %s\n\n" % text['name']
            body = text['description']
            text = title + body
        else:
            text = '# Items\n\n'
        return text

    def add(self, item):
        if isinstance(item, self.type):
            super().add(item)
        elif isinstance(item, dict):
            g = item['name']
            if g is not None:
                self.groups[g] = item['description']

    @staticmethod
    def _getgroup(g):
        if g is not None:
            g = g.split('/')
            if g:
                g = g[-1]
            else:
                g = ''
        return g

    def page(self):
        ret = self.head
        ret = utils.convert(ret)
        ret = utils.get_details(ret)

        ret += '<table>\n'
        ret += (
            '<tr>'
            '<th>Item</th>'
            '<th>Cost</th>'
            '<th>Weight</th>'
            '</tr>\n'
        )

        for item in self.values():
            if not item.item_group:
                ret += item.page()

        ret += '</table>\n'

        with self.db as db:
            groups = db.select("item_groups")
        groups = {item["name"]: item["description"] for item in groups}
        for name in sorted(groups):
            description = groups[name]
            hadany = False
            temp = '<h2>%s</h2>\n' % self._getgroup(name)
            temp += utils.convert(description)
            temp += '<table>\n'
            temp += (
                '<tr>'
                '<th>Item</th>'
                '<th>Cost</th>'
                '<th>Weight</th>'
                '</tr>\n'
            )
            for item in self.values():
                if item.item_group == name:
                    temp += item.page()
                    hadany = True
            temp += '</table>\n'
            if hadany:
                ret += utils.get_details(temp)

        ret = utils.get_details(ret, 'h1')

        return ret
