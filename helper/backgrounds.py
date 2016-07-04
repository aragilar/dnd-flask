from . import utils

def background2html(background):
    summary = '<h2>%s</h2>' % background.get('name', '')
    
    body = '%s\n\n' % '\n'.join(background.get('description', []))
    
    temp = background.get('skills', [])
    if len(temp):
        body += '**Skill Proficiencies:** %s  \n' % utils.choice_list(temp, 'skill')
    
    temp = background.get('tools', [])
    if len(temp):
        body += '**Tool Proficiencies:** %s  \n' % utils.choice_list(temp, 'tool')
    
    temp = background.get('languages', [])
    if len(temp):
        body += '**Languages:** %s  \n' % utils.choice_list(temp, 'language')
    
    temp = background.get('equipment', [])
    if len(temp):
        body += '**Equipment:** %s\n\n' % utils.comma_list(temp)
    
    temp = background.get('features', [])
    for feature in temp:
        body += '*%s*  \n%s\n\n' % (feature[0], '\n'.join(feature[1:]))
    
    body += '*Suggested Characteristics*  \n%s\n\n' % '\n'.join(background.get('characteristics', []))
    
    temp = background.get('personality traits', [])
    if len(temp):
        body += '***\n\n'
        if isinstance(temp, list):
            body += '| d%d | %s |\n' % (len(temp), 'Personality Trait')
            body += '|:---:|:---|\n'
            for x, item in enumerate(temp):
                body += '| %d | %s |\n' % (x+1, item)
        else:
            body += '**Personality Traits**  \n'
            body += str(temp)
        body += '\n'
    
    temp = background.get('ideal', [])
    if len(temp):
        body += '***\n\n'
        if isinstance(temp, list):
            body += '| d%d | %s |\n' % (len(temp), 'Ideal')
            body += '|:---:|:---|\n'
            for x, item in enumerate(temp):
                body += '| %d | %s |\n' % (x+1, item)
        else:
            body += '**Ideals**  \n'
            body += str(temp)
        body += '\n'
    
    temp = background.get('bond', [])
    if len(temp):
        body += '***\n\n'
        if isinstance(temp, list):
            body += '| d%d | %s |\n' % (len(temp), 'Bond')
            body += '|:---:|:---|\n'
            for x, item in enumerate(temp):
                body += '| %d | %s |\n' % (x+1, item)
        else:
            body += '**Bonds**  \n'
            body += str(temp)
        body += '\n'
    
    temp = background.get('flaw', [])
    if len(temp):
        body += '***\n\n'
        if isinstance(temp, list):
            body += '| d%d | %s |\n' % (len(temp), 'Flaw')
            body += '|:---:|:---|\n'
            for x, item in enumerate(temp):
                body += '| %d | %s |\n' % (x+1, item)
        else:
            body += '**Flaws**  \n'
            body += str(temp)
        body += '\n'
    
    temp = background.get('variant', [])
    if len(temp):
        body += '***\n\n'
        body += '\n'.join(temp)
        body += '\n\n'
    
    body += '***\n\n'
    
    body = utils.convert(body)
    
    ret = utils.details_block(summary, body)
    
    return ret

def main(backgrounds, load):
    ret = '<div>\n'
    temp = load('backgrounds.md')
    if temp:
        ret += utils.get_details(utils.get_details(utils.convert(temp)), 'h1')
    else:
        ret += '<h1>Backgrounds</h1>\n'

    for background in sorted(backgrounds.keys()):
        background = backgrounds[background]
        ret += background2html(background)

    ret += '</div>\n'
    
    #ret = load.html_back(top + ret, 'Backgrounds', 'backgrounds/', ['../items.css'])
    return ret
