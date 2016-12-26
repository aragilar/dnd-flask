import os
import re
import json

from . import utils
from . import spells

class Race (utils.Base):
    def page(self):
        # ----#-   Race Description
        ret = "# %s\n\n" % self.name
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
        stats = utils.stats.copy()
        stats['+'] = 'ability_bonus'
        scores = {
            score: getattr(self, name.lower(), 0)
            for score, name in stats.items()
        }
        print(scores)
        if scores and any(scores.values()):
            lst = []
            if all(map(lambda a: scores[a] == 1, utils.statlist)):
                lst.append("your ability scores each increase by 1")
            elif any(map(lambda a: scores[a] if a != '+' else 0, scores)):
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
            if scores['+'] and scores['+'] > 0:
                lst.append('%d different ability scores of your choice increase by 1'
                    % scores.get('+')
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
            if self.size_description:
                ret += '***Size.*** %s\n\n' % self.size_description.format(size=self.size)
            else:
                ret += '***Size.*** Your size is %s.\n\n' % self.size

        # ----#-   Race Speed
        if self.speed is not None:
            if self.speed_description:
                ret += '***Speed.*** %s\n\n' % self.speed_description.format(speed=self.speed)
            else:
                ret += '***Speed.*** Your base walking speed is %s feet.\n\n' % self.speed

        # ----#-   Race Traits
        if self.traits:
            for name, trait in self.traits.items():
                ret += '***%s.*** %s\n\n' % (name, trait.lstrip())

        # ----#-   Race Weapons
        if self.combat_proficiencies:
            ret += ('***%s Combat Training.*** You have proficiency in %s.\n\n'
                % (self.name, utils.comma_list(self.combat_proficiencies))
            )

        # ----#-   Race Tools
        if self.tool_proficiencies and len(self.tool_proficiencies) > 1:
            ret += '***Tool Proficiencies.*** %s.\n\n' % utils.choice_list(self.tool_proficiencies, 'tool')
        elif self.tool_proficiencies:
            ret += ('***Tool Proficiency.*** You gain proficiency with %s.\n\n'
                % str(self.tool_proficiencies[0])
            )

        # ----#-   Race Skills
        if self.skills and len(self.skills) > 1:
            ret += ('***Skills.*** You gain proficiency in %s.\n\n'
                % utils.choice_list(self.skills, 'skill')
            )
        elif self.skills:
            if self.skills[0].isdigit():
                if self.skills[0] == '1':
                    ret += '***Skills.*** You gain proficiency in a skill of your choice.\n\n'
                else:
                    ret += '***Skills.*** You gain proficiency in %s skills of your choice.\n\n' % self.skills[0]
            else:
                ret += '***Skills.*** You gain proficiency in %s.\n\n' % str(self.skills[0])

        # ----#-   Race Feats
        if self.feats and len(self.feats) > 1:
            ret += '***Feats.*** You gain %s.\n\n' % utils.choice_list(self.feats, 'feat')
        elif self.feats:
            if self.feats[0].isdigit():
                if self.feats[0] == '1':
                    ret += '***Feats.*** You gain a feat of your choice.\n\n'
                else:
                    ret += '***Feats.*** You gain %s feats of your choice.\n\n' % self.feats[0]
            else:
                ret += '***Feats.*** You gain the %s feat.\n\n' % str(self.feats[0])

        # ----#-   Race Languages
        if self.languages:
            temp = self.languages[:]
        else:
            temp = []

        if temp and temp[-1].isdigit():
            if temp[-1] == '1':
                temp[-1] = '1 additional language'
            else:
                temp[-1] = '%s additional languages' % temp[-1]

        if temp:
            if self.languages_description:
                ret += '***Languages.*** %s\n\n' % self.languages_description.format(
                    languages=utils.choice_list(temp, 'language')
                )
            elif len(temp) == 1 and temp[0].isdigit():
                if temp[0] == '1':
                    ret += '***Languages.*** You can speak, read, and write 1 language of your choice.\n\n'
                else:
                    ret += '***Languages.*** You can speak, read, and write %s languages of your choice.\n\n' % temp[0]
            else:
                ret += '***Languages.*** You can speak, read, and write %s.\n\n' % utils.comma_list(temp, 'language')

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
