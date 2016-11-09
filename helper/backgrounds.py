import os
import json

from . import utils

class Background (utils.Base):
    def page(self):
        body = '<h2>%s</h2>\n' % self.name

        if self.description:
            body += '%s\n' % utils.convert(self.description)

        if self.skills:
            body += '<p><strong>Skill Proficiencies:</strong> %s</p>\n' % utils.choice_list(self.skills, 'skill')

        if self.tools:
            body += '<p><strong>Tool Proficiencies:</strong> %s</p>\n' % utils.choice_list(self.tools, 'tool')

        if self.languages:
            body += '<p><strong>Languages:</strong> %s</p>\n' % utils.choice_list(self.languages, 'language')

        if self.equipment:
            body += '<p><strong>Equipment:</strong> %s<p>\n' % utils.comma_list(self.equipment)

        for feature in self.features:
            body += '<h3>%s</h3>\n' % feature[0]
            body += utils.convert(feature[1])

        body += '<h3>Suggested Characteristics</h3>\n'
        if self.characteristics:
            body += utils.convert(self.characteristics)

        for temp, title in [
            (self.personality_traits, 'Personality Trait'),
            (self.ideal, 'Ideal'),
            (self.bond, 'Bond'),
            (self.flaw, 'Flaw'),
        ]:
            if temp:
                table = '| d%d | %s |\n' % (len(temp), title)
                table += '|:---:|:---|\n'
                for x, item in enumerate(temp):
                    table += '| %d | %s |\n' % (x+1, item)
                body += utils.convert(table)

        if self.variant:
            body += utils.convert(self.variant)

        return body

class Backgrounds (utils.Group):
    type = Background
    tablename = "backgrounds"
    
    @property
    def head(self):
        return self.get_document("Backgrounds", "Backgrounds")

    def page(self):
        ret = '<div>\n'

        ret += self.head

        body = ''
        for background in self.values():

            body += utils.details_block(background.name, background.page())

        ret += utils.details_group(body)

        ret += '</div>\n'
        return ret
