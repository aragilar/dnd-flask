import re
import multiprocessing.pool
import markdown2

md = markdown2.Markdown(extras = [
'fenced-code-blocks',
'header-ids',
#'smarty-pants',
'tables',
'toc',
'markdown-in-html'
])

convert = md.convert

stats = {
'str': 'Strength',
'dex': 'Dexterity',
'con': 'Constitution',
'int': 'Intelligence',
'wis': 'Wisdom',
'cha': 'Charisma'}
statlist = ['str', 'dex', 'con', 'int', 'wis', 'cha']

ordinals = [
'0th',
'1st',
'2nd',
'3rd',
'4th',
'5th',
'6th',
'7th',
'8th',
'9th',
'10th',
'11th',
'12th',
'13th',
'14th',
'15th',
'16th',
'17th',
'18th',
'19th',
'20th']

experience = [
    0,
    300,
    900,
    2700,
    6500,
    14000,
    23000,
    34000,
    48000,
    64000,
    85000,
    100000,
    120000,
    140000,
    165000,
    195000,
    225000,
    265000,
    305000,
    355000
]

spellslots = [
    [0,0,0,0,0,0,0,0,0],
    [2,0,0,0,0,0,0,0,0],
    [3,0,0,0,0,0,0,0,0],
    [4,2,0,0,0,0,0,0,0],
    [4,3,0,0,0,0,0,0,0],
    [4,3,2,0,0,0,0,0,0],
    [4,3,3,0,0,0,0,0,0],
    [4,3,3,1,0,0,0,0,0],
    [4,3,3,2,0,0,0,0,0],
    [4,3,3,3,1,0,0,0,0],
    [4,3,3,3,2,0,0,0,0],
    [4,3,3,3,2,1,0,0,0],
    [4,3,3,3,2,1,0,0,0],
    [4,3,3,3,2,1,1,0,0],
    [4,3,3,3,2,1,1,0,0],
    [4,3,3,3,2,1,1,1,0],
    [4,3,3,3,2,1,1,1,0],
    [4,3,3,3,2,1,1,1,1],
    [4,3,3,3,3,1,1,1,1],
    [4,3,3,3,3,2,1,1,1],
    [4,3,3,3,3,2,2,1,1]
]

def comma_list(lst, joiner = 'and'):
    if len(lst) > 2 or joiner == None:
        ret = ', '.join(lst[:-1])
        ret += ', '
        if joiner != None:
            ret += '%s ' % joiner
        ret += str(lst[-1])
    elif len(lst) > 0:
        ret = (' %s ' % joiner).join(lst)
    else:
        ret = 'none'
    return ret

def choice_list(lst, type = ''):
    if type != '':
        type = ' ' + type
    if len(lst) > 0:
        if type != '':
            if isinstance(lst[0], str) or lst[0] > 1:
                type += 's'
        if isinstance(lst[0], int) and len(lst) > 1:
            ret = 'Choose %d%s from %s' % (lst[0], type, comma_list(lst[1:]))
        elif isinstance(lst[0], int):
            ret = 'Choose %d%s' % (lst[0], type)
        else:
            ret = comma_list(lst)
    else:
        ret = 'none'
    return ret

def get_details(text, detltag='h2', splttag=None):
    if splttag is not None:
        blocks = text.split('<{}'.format(splttag))
    else:
        blocks = [text]
    
    for x in range(len(blocks)):
        text = blocks[x]
        text, n = re.subn('(<{0}.+?>.*?</{0}>)'.format(detltag), '</details>\n<details>\n<summary>\\1</summary>\n', text)
        
        if n > 0:
            text = text.replace('</details>\n', '', 1)
            text += '</details>\n'

        blocks[x] = text
    
    if splttag is not None:
        text = '<{}'.format(splttag).join(blocks)
    else:
        text = blocks[0]
    return text

def asynclist(func, lst):
    try:
        with multiprocessing.pool.ThreadPool(processes=len(lst)) as pool:
            new = pool.map(func, lst)
    except:
        new = map(func, lst)
    return new
