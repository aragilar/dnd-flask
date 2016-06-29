from . import utils

def background2html(background):
    ret = '<details><summary><h2>%s</summary>\n\n' % background.get('name', '')
    
    ret += '%s\n\n' % '\n'.join(background.get('description', []))
    
    temp = background.get('skills', [])
    if len(temp):
        ret += '**Skill Proficiencies:** %s  \n' % utils.choice_list(temp, 'skill')
    
    temp = background.get('tools', [])
    if len(temp):
        ret += '**Tool Proficiencies:** %s  \n' % utils.choice_list(temp, 'tool')
    
    temp = background.get('languages', [])
    if len(temp):
        ret += '**Languages:** %s  \n' % utils.choice_list(temp, 'language')
    
    temp = background.get('equipment', [])
    if len(temp):
        ret += '**Equipment:** %s\n\n' % utils.comma_list(temp)
    
    temp = background.get('features', [])
    for feature in temp:
        ret += '*%s*  \n%s\n\n' % (feature[0], '\n'.join(feature[1:]))
    
    ret += '*Suggested Characteristics*  \n%s\n\n' % '\n'.join(background.get('characteristics', []))
    
    temp = background.get('personality traits', [])
    if len(temp):
        ret += '***\n\n'
        if isinstance(temp, list):
            ret += '| d%d | %s |\n' % (len(temp), 'Personality Trait')
            ret += '|:---:|:---|\n'
            for x, item in enumerate(temp):
                ret += '| %d | %s |\n' % (x+1, item)
        else:
            ret += '**Personality Traits**  \n'
            ret += str(temp)
        ret += '\n'
    
    temp = background.get('ideal', [])
    if len(temp):
        ret += '***\n\n'
        if isinstance(temp, list):
            ret += '| d%d | %s |\n' % (len(temp), 'Ideal')
            ret += '|:---:|:---|\n'
            for x, item in enumerate(temp):
                ret += '| %d | %s |\n' % (x+1, item)
        else:
            ret += '**Ideals**  \n'
            ret += str(temp)
        ret += '\n'
    
    temp = background.get('bond', [])
    if len(temp):
        ret += '***\n\n'
        if isinstance(temp, list):
            ret += '| d%d | %s |\n' % (len(temp), 'Bond')
            ret += '|:---:|:---|\n'
            for x, item in enumerate(temp):
                ret += '| %d | %s |\n' % (x+1, item)
        else:
            ret += '**Bonds**  \n'
            ret += str(temp)
        ret += '\n'
    
    temp = background.get('flaw', [])
    if len(temp):
        ret += '***\n\n'
        if isinstance(temp, list):
            ret += '| d%d | %s |\n' % (len(temp), 'Flaw')
            ret += '|:---:|:---|\n'
            for x, item in enumerate(temp):
                ret += '| %d | %s |\n' % (x+1, item)
        else:
            ret += '**Flaws**  \n'
            ret += str(temp)
        ret += '\n'
    
    temp = background.get('variant', [])
    if len(temp):
        ret += '***\n\n'
        ret += '\n'.join(temp)
        ret += '\n\n'
    
    ret += '***\n\n'
    
    ret += '</details>'
    ret = utils.convert(ret)
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
