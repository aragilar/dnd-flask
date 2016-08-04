import os
import re

from . import utils
from . import spells

class Race (utils.Base):
    ability_scores = {}
    age = None
    alignment = None
    combat_proficiencies = []
    description = []
    feats = []
    languages = []
    languages_description = None
    skills = []
    size = 'medium'
    size_description = 'Your size is {size}.'
    speed = 30
    speed_description = 'Your base walking speed is {speed} feet.'
    tool_proficiencies = []
    traits = []
    
    def __str__(self):
        ret = '<div>\n'
        
        # ----#-   Race Description
        temp = utils.convert('\n'.join(self.description))
        ret += utils.get_details(temp, 'h1') + '\n\n'
        
        # ----#-   Race Features
        ret += self.features2html()
        ret += '</div>\n'
        
        ret = spells.handle_spells(ret, self.spell_list)
        
        # ----#-   Subrace
        for subrace in self.children.values():
            ret += str(subrace)
        
        return ret
    
    def features2html(self):
        ret = ''
        
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
            ret += '**Ability Score Increase.** %s\n\n' % lst
        
        # ----#-   Race Age
        if self.age is not None:
            ret += '**Age.** %s\n\n' % self.age
        
        # ----#-   Race Alignment
        if self.alignment is not None:
            ret += '**Alignment.** %s\n\n' % self.alignment
        
        # ----#-   Race Size
        if self.size is not None:
            ret += '**Size.** %s\n\n' % self.size_description.format(size=self.size)
        
        # ----#-   Race Speed
        if self.speed is not None:
            ret += '**Speed.** %s\n\n' % self.speed_description.format(speed=self.speed)
        
        # ----#-   Race Traits
        for trait in self.traits:
            ret += '**%s.** %s\n\n' % (trait[0], '\n'.join(trait[1:]))
        
        # ----#-   Race Weapons
        if self.combat_proficiencies:
            ret += ('**%s Combat Training.** You have proficiency in %s.\n\n'
                % (self.name, utils.comma_list(self.combat_proficiencies))
            )
        
        # ----#-   Race Tools
        if len(self.tool_proficiencies) > 1:
            ret += '**Tool Proficiencies.** %s.\n\n' % utils.choice_list(self.tool_proficiencies, 'tool')
        elif self.tool_proficiencies:
            ret += ('**Tool Proficiency.** You gain proficiency with %s.\n\n'
                % str(self.tool_proficiencies[0])
            )
        
        # ----#-   Race Skills
        if len(self.skills) > 1:
            ret += ('**Skills.** You gain proficiency in %s.\n\n'
                % utils.choice_list(self.skills, 'skill')
            )
        elif self.skills:
            if isinstance(self.skills[0], int):
                if self.skills[0] == 1:
                    ret += '**Skills.** You gain proficiency in a skill of your choice.\n\n'
                else:
                    ret += '**Skills.** You gain proficiency in %d skills of your choice.\n\n' % self.skills[0]
            else:
                ret += '**Skills.** You gain proficiency in %s.\n\n' % str(self.skills[0])
        
        # ----#-   Race Feats
        if len(self.feats) > 1:
            ret += '**Feats.** You gain %s.\n\n' % utils.choice_list(self.feats, 'feat')
        elif len(self.feats):
            if isinstance(self.feats[0], int):
                if self.feats[0] == 1:
                    ret += '**Feats.** You gain a feat of your choice.\n\n'
                else:
                    ret += '**Feats.** You gain %d feats of your choice.\n\n' % self.feats[0]
            else:
                ret += '**Feats.** You gain the %s feat.\n\n' % str(self.feats[0])
        
        # ----#-   Race Languages
        temp = self.languages[:]
        if len(temp) and isinstance(temp[-1], int):
            if temp[-1] == 1:
                temp[-1] = '%d additional language' % temp[-1]
            else:
                temp[-1] = '%d additional languages' % temp[-1]
        
        if temp:
            tempstr = self.languages_description
            if tempstr is not None:
                ret += '**Languages.** %s\n\n' % tempstr.format(
                    languages=utils.choice_list(temp, 'language')
                )
            else:
                ret += ('**Languages.** You can speak, read, and write %s.\n\n'
                    % utils.choice_list(temp, 'language')
                )
        
        ret = utils.md.convert(ret)
        
        return ret

class SubRace (Race):
    subclass = None
    
    size = None
    speed = None

    def __str__(self):
        summary = '<h1 id="%s">%s</h1>' % (utils.slug(self.name), self.name)
        desc = self.description
        desc = '\n'.join(desc)
        desc = utils.convert(desc)
        ret = utils.details_group(utils.details_block(summary, desc))
        ret += self.features2html()
        
        ret = spells.handle_spells(ret, self.spell_list)
        
        ret = '<div>\n%s</div>\n' % ret
        
        return ret

Race.subclass = SubRace

class Races (utils.Group):
    type = Race
    head = '<h1>Races</h1>\n'
    
    def __init__(self, folder=None, sources=None):
        super().__init__(folder, sources)

        if folder:
            path = os.path.join(folder, 'documentation/races.md')
            if os.path.exists(path):
                with open(path, 'r') as f:
                    data = f.read()
                data = utils.convert(data)
                data = utils.get_details(data)
                data = utils.get_details(data, 'h1')
                self.head = data
