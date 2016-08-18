import os

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
        body = '<h2>%s</h2>\n' % self.name
        
        body += '%s\n' % utils.convert('\n'.join(self.description))
        
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
        
        return body

class Backgrounds (utils.Group):
    type = Background
    head = '<h1>Backgrounds</h1>\n'
    
    def __init__(self, folder=None, sources=None):
        super().__init__(folder, sources)
        if folder:
            folder = os.path.join(folder, 'documentation/backgrounds.md')
            if os.path.exists(folder):
                with open(folder, 'r') as f:
                    data = f.read()
                data = utils.convert(data)
                data = utils.get_details(data)
                data = utils.get_details(data, 'h1')
                self.head = data

    def page(self):
        ret = '<div>\n'
        
        ret += self.head

        body = ''
        for background in self.values():
            
            body += utils.details_block(background.name, str(background))
        
        ret += utils.details_group(body)

        ret += '</div>\n'
        return ret
