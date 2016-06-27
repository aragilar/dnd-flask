import re
import utils

def weapon2html(weapon):
    ret = '<tr>\n'
    
    ret += '<th>%s</th>\n' % weapon.get('name', '')
    
    temp = weapon.get('cost', 0.0)
    if temp > 0:
        if temp < 0.1:
            ret += '<td>%d cp</td>\n' % int(temp * 100)
        elif temp < 1:
            ret += '<td>%d sp</td>\n' % int(temp * 10)
        else:
            ret += '<td>%d gp</td>\n' % int(temp)
    else:
        ret += '<td>-</td>\n'
    
    ret += '<td>%s %s</td>' % (weapon.get('damage', ''), weapon.get('damage type', 'unknown'))
    
    ret += '<td>%s lb.</td>\n' % weapon.get('weight', '0')
    
    ret += '<td>%s</td>\n' % ', '.join(weapon.get('properties', ['-']))
    
    ret += '</tr>\n'
    return ret

def armor2html(armor):
    ret = '<tr>\n'
    
    ret += '<th>%s</th>' % armor.get('name', '')
    
    temp = armor.get('cost', 0.0)
    if temp > 0:
        if temp < 0.1:
            ret += '<td>%d cp</td>\n' % int(temp * 100)
        elif temp < 1:
            ret += '<td>%d sp</td>\n' % int(temp * 10)
        else:
            ret += '<td>%d gp</td>\n' % int(temp)
    else:
        ret += '<td>-</td>\n'
    
    ret += '<td>%s</td>\n' % armor.get('ac', '-')
    
    temp = armor.get('strength', 0)
    if temp > 0:
        ret += '<td>%d</td>\n' % temp
    else:
        ret += '<td>-</td>\n'
    
    if armor.get('stealth'):
        ret += '<td>Disadvantage</td>\n'
    else:
        ret += '<td>-</td>\n'
    
    ret += '<td>%s</td>\n' % armor.get('weight', 0)
    
    ret += '<td>%s</td>\n' % armor.get('note', '-')
    
    ret += '</tr>\n'
    return ret

def item2html(item):
    ret = '<tr>\n'
    
    if item.get('group', False):
        temp = item.get('description')
        
        if temp != None:
            temp = utils.convert(str(temp))
            temp += '\n\n'
        else:
            temp = ''
        
        temp += '<table>\n<tr><th>Item</th><th>Cost</th><th>Weight</th></tr>\n'
        
        for key in sorted(filter(lambda a: a[0].isupper() or a[0].isdigit(), item.keys())):
            temp += item2html(item[key]) + '\n'
        
        temp += '</table>\n'
        
        ret += '<td colspan="3"><details><summary><strong><em>%s</em></strong></summary>\n%s\n</details></td></tr>\n' % (item.get('name', ''), temp)
    else:
        temp = item.get('description')
        if temp == None:
            ret += '<td>%s</td>' % item.get('name', '')
        else:
            ret += '<td><details><summary>%s</summary>\n%s\n</details></td>' % (item.get('name', ''), utils.convert(str(temp)))
        
        temp = item.get('cost', 0.0)
        if temp > 0:
            try:
                if temp < 0.1:
                    ret += '<td>%d cp</td>\n' % int(temp * 100)
                elif temp < 1:
                    ret += '<td>%d sp</td>\n' % int(temp * 10)
                else:
                    ret += '<td>%d gp</td>\n' % int(temp)
            except ValueError:
                ret += '<td>%s</td>\n' % str(temp)
        else:
            ret += '<td>-</td>\n'
        
        ret += '<td>%s</td>\n' % item.get('weight', '-')
    
    ret += '</tr>\n'
    return ret

def main(weapons, armors, items, load):
    ret = '<div id="items-div">\n'
    
    if len(items):
        temp = load('equipment.md')
        if temp:
            temp = utils.get_details(utils.convert(temp))
        else:
            temp = '<h1>Equipment</h1>\n'
        temp += '<table id="item-table">\n'
        temp += '<tr><th>Item</th><th>Cost</th><th>Weight</th></tr>\n'
        for item in sorted(items):
            temp += item2html(items[item])
        temp += '</table>\n'
        ret += utils.get_details(temp, 'h1')
    
    temp = load('equipment-packs.md')
    if temp:
        ret += utils.get_details(utils.get_details(utils.convert(temp)), 'h1')
    
    if len(weapons):
        temp = ''
        t = load('weapons.md')
        if t:
            temp += t
            temp += '\n\n'
        else:
            temp += '<h1>Weapons</h1>\n'
        del t
        
        temp += '## Special\n\n'
        for item in sorted(weapons.keys()):
            if weapons[item].has_key('special'):
                temp += '**%s** %s\n\n' % (item, weapons[item]['special'])
        temp = utils.get_details(utils.convert(temp))
        
        temp += '<table id="weapons-table">\n'
        temp += '<tr><th>Name</th><th>Cost</th><th>Damage</th><th>Weight</th><th>Properties</th></tr>'
        martial_melee = []
        martial_ranged = []
        simple_melee = []
        simple_ranged = []
        other = []
        for weapon in sorted(weapons.keys()):
            weapon = weapons[weapon]
            type = weapon.get('type', '')
            range = weapon.get('ranged', False)
            if type == 'martial':
                if not range:
                    martial_melee.append(weapon)
                else:
                    martial_ranged.append(weapon)
            elif type == 'simple':
                if not range:
                    simple_melee.append(weapon)
                else:
                    simple_ranged.append(weapon)
            else:
                other.append(weapon)
        
        for name, lst in [('Simple Melee', simple_melee), ('Simple Ranged', simple_ranged), ('Martial Melee', martial_melee), ('Martial Ranged', martial_ranged), ('Other', other)]:
            if len(lst):
                temp += '<tr><th colspan="100">%s</th></tr>\n' % name
                for weapon in lst:
                    temp += weapon2html(weapon)
        
        temp += '</table>\n'
        ret += utils.get_details(temp, 'h1')
    
    if len(armors):
        temp = ''
        t = load('armors.md')
        if t:
            temp += t
            temp += '\n\n'
        else:
            temp += '<h1>Armors</h1>\n'
        del t
        temp = utils.get_details(utils.convert(temp))
        
        temp += '<table id="armor-table">\n'
        temp += '<tr><th>Armor</th><th>Cost</th><th>Armor Class (ac)</th><th>Strength</th><th>Stealth</th><th>Weight</th><th>Note</th></tr>'
        light = []
        medium = []
        heavy = []
        other = []
        alist = map(lambda a: armors[a], armors.keys())
        alist = sorted(alist, key = lambda a: not a.get('stealth', False))
        alist = sorted(alist, key = lambda a: a.get('ac', ''))
        alist = sorted(alist, key = lambda a: a.get('cost', 0.0) if a.get('cost', 0.0) > 0 else float('inf'))
        for armor in alist:
            type = armor.get('type', '')
            if type == 'light':
                light.append(armor)
            elif type == 'medium':
                medium.append(armor)
            elif type == 'heavy':
                heavy.append(armor)
            else:
                other.append(armor)
        
        for name, lst in [('Light', light), ('Medium', medium), ('Heavy', heavy), ('Other', other)]:
            if len(lst):
                temp += '<tr><th colspan="100">%s</th></tr>\n' % name
                for armor in lst:
                    temp += armor2html(armor)
        temp += '</table>\n'
        ret += utils.get_details(temp, 'h1')
    
    ret += '</div>\n'
    return ret
