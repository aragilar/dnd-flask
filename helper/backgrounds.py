from . import utils

class Background (utils.Base):
    bond = []
    characteristics = []
    equipment = []
    features = []
    flaw = []
    ideal = []
    languages = []
    personality_traits = []
    skills = []
    tools = []
    variant = None

    def __str__(self):
        summary = '<h2>%s</h2>' % self.name
        
        body = '%s\n' % utils.convert('\n'.join(self.description))
        
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
            body += utils.convert('\n'.join(feature[1:]))
        
        body += '<h3>Suggested Characteristics</h3>\n'
        body += utils.convert('\n'.join(self.characteristics))
        
        for temp, title in [
            (self.personality_traits, 'Personality Trait'),
            (self.ideal, 'Ideal'),
            (self.bond, 'Bond'),
            (self.flaw, 'Flaw'),
        ]:
            if temp:
                if isinstance(temp, list):
                    table = '| d%d | %s |\n' % (len(temp), title)
                    table += '|:---:|:---|\n'
                    for x, item in enumerate(temp):
                        table += '| %d | %s |\n' % (x+1, item)
                    body += utils.convert(table)
        
        if self.variant:
            body += utils.convert('\n'.join(self.variant))
        
        ret = utils.details_group(utils.details_block(summary, body))
        
        return ret

class Backgrounds (utils.Group):
    type = Background

    def page(self, load):
        ret = '<div>\n'
        temp = load('backgrounds.md')
        if temp:
            ret += utils.get_details(utils.get_details(utils.convert(temp)), 'h1')
        else:
            ret += '<h1>Backgrounds</h1>\n'

        for background in self:
            ret += str(background)

        ret += '</div>\n'
        return ret
