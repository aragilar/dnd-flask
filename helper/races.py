import os
import re
import json

from . import utils
from . import spells

class Race (utils.Base):
    def __init__(self, parent, d):
        for key, value in {
            "description": "",
            "traits_description": "",
            "age": "",
            "alignment": "",
            "size": "",
            "speed": 30,
            "subrace": "",
        }.items():
            if d[key] is None:
                d[key] = value

        for key in [
            "combat_proficiencies",
            "tool_proficiencies",
            "skills",
            "feats",
            "languages",
        ]:
            d[key] = [] if d[key] is None else d[key].split("\v")

        d["ability_scores"] = {} if d["ability_scores"] is None else json.loads(d["ability_scores"])
        d["traits"] = [] if d["traits"] is None else json.loads(d["traits"])

        super().__init__(parent, d)

    def page(self):
        ret = '<div>\n'

        # ----#-   Race Description
        temp = utils.convert(self.description)
        ret += utils.get_details(temp, 'h1') + '\n\n'

        # ----#-   Race Features
        ret += self.features2html()
        ret += '</div>\n'

        ret = spells.handle_spells(ret, self.parent.get_spell_list(spells.Spells))

        # ----#-   Subrace
        for subrace in self.children.values():
            ret += subrace.page()

        return ret

    def features2html(self):
        ret = ''

        if self.traits_description is not None:
            ret += self.traits_description + '\n\n'

        # ----#-   Race Ability Scores
        scores = self.ability_scores
        if sum(map(lambda a: scores[a], scores)) > 0:
            lst = []
            if sum(map(lambda a: scores[a] if a != '+' else 0, scores)) > 0:
                if all(map(lambda a: scores[a] == 1, utils.statlist)):
                    lst.append("your ability scores each increase by 1")
                else:
                    for i in utils.statlist:
                        if scores.get(i) > 0:
                            lst.append('your %s score increases by %d' % (
                                utils.stats[i],
                                scores.get(i)
                            ))
                if scores.get('+') > 0:
                    lst.append('%d other ability scores of your choice increase by 1'
                        % scores.get('+')
                    )
            elif scores.get('+') > 0:
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
        for trait in self.traits:
            ret += '***%s.*** %s\n\n' % (trait[0], '\n'.join(trait[1:]))

        # ----#-   Race Weapons
        if self.combat_proficiencies:
            ret += ('***%s Combat Training.*** You have proficiency in %s.\n\n'
                % (self.name, utils.comma_list(self.combat_proficiencies))
            )

        # ----#-   Race Tools
        if len(self.tool_proficiencies) > 1:
            ret += '***Tool Proficiencies.*** %s.\n\n' % utils.choice_list(self.tool_proficiencies, 'tool')
        elif self.tool_proficiencies:
            ret += ('***Tool Proficiency.*** You gain proficiency with %s.\n\n'
                % str(self.tool_proficiencies[0])
            )

        # ----#-   Race Skills
        if len(self.skills) > 1:
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
        if len(self.feats) > 1:
            ret += '***Feats.*** You gain %s.\n\n' % utils.choice_list(self.feats, 'feat')
        elif len(self.feats):
            if self.feats[0].isdigit():
                if self.feats[0] == '1':
                    ret += '***Feats.*** You gain a feat of your choice.\n\n'
                else:
                    ret += '***Feats.*** You gain %s feats of your choice.\n\n' % self.feats[0]
            else:
                ret += '***Feats.*** You gain the %s feat.\n\n' % str(self.feats[0])

        # ----#-   Race Languages
        temp = self.languages[:]
        if len(temp) and temp[-1].isdigit():
            if temp[-1] == '1':
                temp[-1] = '%s additional language' % temp[-1]
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

    def __init__(self, parent, d):
        for key, value in {
            "description": "",
        }.items():
            if d[key] is None:
                d[key] = value

        for key in [
            "combat_proficiencies",
            "tool_proficiencies",
            "skills",
            "feats",
            "languages",
        ]:
            d[key] = [] if d[key] is None else d[key].split("\v")

        d["ability_scores"] = {} if d["ability_scores"] is None else json.loads(d["ability_scores"])
        d["traits"] = [] if d["traits"] is None else json.loads(d["traits"])

        utils.Base.__init__(self, parent, d)

    def page(self):
        summary = '<h1 id="%s">%s</h1>' % (utils.slug(self.name), self.name)
        desc = utils.convert(self.description)
        ret = utils.details_group(utils.details_block(summary, desc))
        ret += self.features2html()

        ret = spells.handle_spells(ret, self.parent.get_spell_list(spells.Spells))

        ret = '<div>\n%s</div>\n' % ret

        return ret

class Races (utils.Group):
    type = Race
    subtype = SubRace
    tablename = "races"
    
    @property
    def head(self):
        return self.get_document("Races", "Races")
