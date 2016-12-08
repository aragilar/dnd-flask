import os
import json

from . import utils

class Background (utils.Base):
    def md(self):
        body = '# %s\n\n' % self.name

        if self.description:
            body += '%s\n' % utils.convert(self.description)

        if self.skills:
            body += '**Skill Proficiencies:** %s\n\n' % utils.choice_list(self.skills, 'skill')

        if self.tools:
            body += '**Tool Proficiencies:** %s\n\n' % utils.choice_list(self.tools, 'tool')

        if self.languages:
            body += '**Languages:** %s\n\n' % utils.choice_list(self.languages, 'language')

        if self.equipment:
            body += '**Equipment:** %s\n\n' % utils.comma_list(self.equipment)

        for feature in self.features:
            body += '## %s\n\n' % feature[0]
            body += feature[1] + '\n\n'

        body += '## Suggested Characteristics\n\n'
        if self.characteristics:
            body += self.characteristics + '\n\n'

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
                body += table + '\n\n'

        if self.variant:
            body += self.variant + '\n\n'

        return body

    def page(self):
        ret = self.md()
        ret = utils.convert(ret)
        return ret

class Backgrounds (utils.Group):
    type = Background
    singular = "Background"
    plural = "Backgrounds"
    tables = [{
        "table": plural,
        "fields": utils.collections.OrderedDict([
            ("name", str),
            ("source", str),
            ("sort_index", int),
            ("description", str),
            ("skills", str),
            ("tools", str),
            ("languages", str),
            ("equipment", str),
            ("features", str),
            ("characteristics", str),
            ("personality_traits", str),
            ("ideal", str),
            ("bond", str),
            ("flaw", str),
            ("variant", str),
        ]),
        "constraints": {
            "name": "PRIMARY KEY NOT NULL",
            "source": "NOT NULL",
            "description": "NOT NULL",
        }
    }]

    @property
    def head(self):
        return self.get_document("Backgrounds", "Backgrounds")

    def page(self):
        ret = self.head

        body = ''
        for background in self.values():

            body += utils.details_block(background.name, background.page())

        ret += utils.details_group(body)

        return ret
