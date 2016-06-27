import re
import utils

def features2html(race):
    ret = ''
    
    # ----#-   Race Ability Scores
    scores = race.get('ability scores', {})
    if sum(map(lambda a: scores[a], scores)) > 0:
        lst = []
        if sum(map(lambda a: scores[a] if a != '+' else 0, scores)) > 0:
            for i in utils.statlist:
                if scores.get(i) > 0:
                    lst.append('your %s score increases by %d' % (utils.stats[i], scores.get(i)))
            if scores.get('+') > 0:
                lst.append('%d other ability scores of your choice increase by 1' % scores.get('+'))
        elif scores.get('+') > 0:
            lst.append('%d different ability scores of your choice increase by 1' % scores.get('+'))
        lst = utils.comma_list(lst)
        lst = lst[0].upper() + lst[1:] + '.'
        ret += '**Ability Score Increase.** %s\n\n' % lst
    
    # ----#-   Race Age
    temp = race.get('age')
    if temp != None:
        ret += '**Age.** %s\n\n' % temp
    
    # ----#-   Race Alignment
    temp = race.get('alignment')
    if temp != None:
        ret += '**Alignment.** %s\n\n' % temp
    
    # ----#-   Race Size
    temp = race.get('size description')
    if temp != None:
        ret += '**Size.** %s\n\n' % temp.format(**race)
    else:
        temp = race.get('size')
        if temp != None:
            ret += '**Size.** Your size is %s.\n\n' % str(temp)
    
    # ----#-   Race Speed
    temp = race.get('speed description')
    if temp != None:
        ret += '**Speed.** %s\n\n' % temp.format(**race)
    else:
        temp = race.get('speed')
        if temp != None:
            ret += '**Speed.** Your base walking speed is %s feet.\n\n' % str(temp)
    
    # ----#-   Race Traits
    temp = race.get('traits-data', {})
    for trait in race.get('traits', []):
        tempstr = '**%s.** %s\n\n' % (trait, '\n'.join(temp.get(trait, ['Unknown Trait'])))
        ret += tempstr
        
    
    # ----#-   Race Weapons
    temp = race.get('combat proficiencies', [])
    if len(temp) > 0:
        ret += '**%s Combat Training.** You have proficiency in %s.\n\n' % (race.get('name', ''), utils.comma_list(temp))
    
    # ----#-   Race Tools
    temp = race.get('tool proficiencies', [])
    if len(temp) > 1:
        ret += '**Tool Proficiencies.** %s.\n\n' % utils.choice_list(temp, 'tool')
    elif len(temp):
        ret += '**Tool Proficiency.** You gain proficiency with %s.\n\n' % str(temp[0])
    
    # ----#-   Race Skills
    temp = race.get('skills', [])
    if len(temp) > 1:
        ret += '**Skills.** You gain proficiency in %s.\n\n' % utils.choice_list(temp, 'skill')
    elif len(temp):
        if isinstance(temp[0], int):
            if temp[0] > 1:
                ret += '**Skill.** You gain proficiency in %d skills.\n\n' % temp[0]
            else:
                ret += '**Skill.** You gain proficiency in %d skill.\n\n' % temp[0]
        else:
            ret += '**Skill.** You gain proficiency in %s.\n\n' % str(temp[0])
    
    # ----#-   Race Feats
    temp = race.get('feats', [])
    if len(temp) > 1:
        ret += '**Feats.** You gain %s.\n\n' % utils.choice_list(temp, 'feat')
    elif len(temp):
        if isinstance(temp[0], int):
            if temp[0] > 1:
                ret += '**Feat.** You gain %d feats.\n\n' % temp[0]
            else:
                ret += '**Feat.** You gain %d feat.\n\n' % temp[0]
        else:
            ret += '**Feat.** You gain the %s feat.\n\n' % str(temp[0])
    
    # ----#-   Race Languages
    temp = race.get('languages', [])
    if len(temp) and isinstance(temp[-1], int):
        if temp[-1] != 1:
            temp[-1] = '%d additional languages' % temp[-1]
        else:
            temp[-1] = '%d additional language' % temp[-1]
    if len(temp):
        tempstr = race.get('languages description')
        if tempstr != None:
            ret += '**Languages.** %s\n\n' % tempstr.format(languages = utils.choice_list(temp, 'language'))
        else:
            if len(temp) > 1:
                ret += '**Languages.** You can speak, read, and write %s.\n\n' % utils.choice_list(temp, 'language')
            else:
                ret += '**Language.** You can speak, read, and write %s.\n\n' % str(temp[0])
    
    ret = utils.md.convert(ret)
    
    return ret

def race2html(race, spell_list):
    ret = ''
    ret += '<div>\n'
    
    # ----#-   Race Description
    temp = utils.convert(race.get('description', ''))
    ret += utils.get_details(temp, 'h1') + '\n\n'
    ret += '</div>\n\n'
    
    # ----#-   Race Features
    ret += '<div>\n'
    ret += features2html(race)
    ret += '</div>\n'
    
    subraces = race.get('subrace', {})
    for subrace in subraces:
        subrace = subraces.get(subrace, {})
        
        ret += '<div>\n'
        ret += '<details><summary><h2>%s</h2></summary>\n' % subrace.get('name', '')
        ret += utils.convert(subrace.get('description', ''))
        ret += '</details>\n'
        ret += features2html(subrace)
        ret += '</div>\n'
    
    ret = utils.handle_spells(ret, spell_list)
    
    return ret
