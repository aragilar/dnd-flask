from collections import OrderedDict

from . import utils
from . import spells

class Race (utils.Base):
    def page(self):
        # ----#-   Race Description
        ret = "# %s\n\n" % self.name
        if self.description:
            ret += self.description
        ret = utils.convert(ret)
        ret = utils.get_details(ret, 'h1') + '\n\n'

        # ----#-   Race Features
        ret += self.features2html()
        ret = '<section class="container">\n%s</section>\n' % ret

        ret = spells.handle_spells(ret, self.parent.get_spell_list(spells.Spells))

        # ----#-   Subrace
        if self.children:
            for subrace in self.children.values():
                ret += subrace.page()

        return ret

    def features2html(self):
        ret = ''

        if self.traits_description is not None:
            ret += self.traits_description + '\n\n'

        # ----#-   Race Ability Scores
        scores = OrderedDict(
            (stat, getattr(self, name.lower(), 0))
            for stat, name in utils.stats.items()
        )
        scores['ability_bonus'] = self.ability_bonus
        for key in scores:
            if scores[key] is None:
                scores[key] = 0
        if any(scores.values()):
            lst = []
            if all(scores[a] == 1 for a in utils.stats):
                lst.append("your ability scores each increase by 1")
            elif any(scores[a] for a in utils.stats):
                for i in utils.statlist:
                    score = scores.get(i, 0)
                    if score:
                        operator = None
                        if score > 0:
                            operator = "increases"
                        else:
                            operator = "decreases"
                            score *= -1
                        lst.append('your %s score %s by %d' % (
                            utils.stats[i],
                            operator,
                            score,
                        ))
            if scores['ability_bonus'] > 0:
                lst.append('%d different ability scores of your choice increase by 1'
                    % scores['ability_bonus']
                )
            lst = utils.comma_list(lst)
            lst = lst[0].upper() + lst[1:] + '.'
            ret += '***Ability Score Increase.*** %s\n\n' % lst

        # ----#-   Race Age
        if self.age is not None:
            ret += '***Age.*** %s\n\n' % self.age

        # ----#-   Race Alignment
        if self.alignment is not None:
            ret += '***Alignment.*** %s\n\n' % self.alignment

        # ----#-   Race Size
        if self.size is not None:
            ret += '***Size.*** %s\n\n' % self.size

        # ----#-   Race Speed
        if self.speed is not None:
            ret += '***Speed.*** %s\n\n' % self.speed

        # ----#-   Race Traits
        if self.traits:
            for name, trait in self.traits.items():
                ret += '***%s.*** %s\n\n' % (name, trait.lstrip())

        # ----#-   Race Languages
        if self.languages:
            ret += '***Languages.*** %s\n\n' % self.languages

        if hasattr(self, "subrace") and self.subrace:
            ret += '***Subrace.*** %s\n\n' % self.subrace

        ret = utils.md.convert(ret)

        return ret

class SubRace (Race):
    subclass = None

    size = None
    speed = None

    def page(self):
        summary = '<h1 id="%s">%s</h1>' % (utils.slug(self.name), self.name)
        if self.description:
            desc = utils.convert(self.description)
        else:
            desc = '\n\n'
        ret = utils.details_group(utils.details_block(summary, desc))
        ret += self.features2html()

        ret = spells.handle_spells(ret, self.parent.get_spell_list(spells.Spells))

        ret = '<section class="container">\n%s</section>\n' % ret

        return ret

class Races (utils.Group):
    type = Race
    subtype = SubRace
    singular = "Race"
    plural = "Races"
    tables = [
    {
        "table": "sub" + plural,
        "fields": utils.OrderedDict([
            ("race", str),
            ("name", str),
            ("source", str),
            ("sort_index", int),
            ("description", str),
            ("traits_description", str),
            ("strength", int),
            ("dexterity", int),
            ("constitution", int),
            ("intelligence", int),
            ("wisdom", int),
            ("charisma", int),
            ("ability_bonus", int),
            ("age", str),
            ("alignment", str),
            ("size", str),
            ("size_description", str),
            ("speed", int),
            ("speed_description", str),
            ("traits", str),
            ("combat_proficiencies", str),
            ("tool_proficiencies", str),
            ("skills", str),
            ("feats", str),
            ("languages", str),
            ("languages_description", str),
        ]),
        "constraints": {
            "race": "REFERENCES %s(name)" % plural,
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
        }
    },
    {
        "table": plural,
        "fields": utils.OrderedDict([
            ("name", str),
            ("source", str),
            ("sort_index", int),
            ("description", str),
            ("traits_description", str),
            ("strength", int),
            ("dexterity", int),
            ("constitution", int),
            ("intelligence", int),
            ("wisdom", int),
            ("charisma", int),
            ("ability_bonus", int),
            ("age", str),
            ("alignment", str),
            ("size", str),
            ("size_description", str),
            ("speed", int),
            ("speed_description", str),
            ("traits", str),
            ("combat_proficiencies", str),
            ("tool_proficiencies", str),
            ("skills", str),
            ("feats", str),
            ("languages", str),
            ("languages_description", str),
            ("subrace", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
        }
    }
    ]

    @property
    def head(self):
        return self.get_document("Races", "Races")
