import re
import collections
try:
    import multiprocessing.pool
except:
    class multiprocessing (object):
        pool = False
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

stats = collections.OrderedDict([
    ('str', 'Strength'),
    ('dex', 'Dexterity'),
    ('con', 'Constitution'),
    ('int', 'Intelligence'),
    ('wis', 'Wisdom'),
    ('cha', 'Charisma')
])
statlist = stats.keys()

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

def slug(s):
    r"""
    gets a "slug", a filename compatible
    version of a string
    """
    s = s.lower()
    s = s.replace(' ', '-')
    s = s.replace("'", '')
    s = s.replace(',', '')
    s = s.replace('/', '-')
    return s

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
    if lst:
        choose = None
        for x, item in enumerate(lst):
            if isinstance(item, int):
                choose = x
                break
        
        if (type and choose is not None
                and lst[choose] > 1):
            type += 's'
        
        if choose is not None and len(lst) > 1:
            if choose == 0:
                ret = 'Choose %d%s from %s' % (
                    lst[0],
                    type,
                    comma_list(lst[1:])
                )
            else:
                ret = '%s, and %d%s from %s' % (
                    comma_list(lst[:choose]),
                    lst[choose],
                    type,
                    comma_list(lst[choose+1:]))
        elif choose is not None:
            if lst[choose] > 1:
                ret = 'Choose any %d%s' % (lst[choose], type)
            else:
                ret = 'Choose any%s' % type
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
    
    finder = re.compile('(<{0}.+?>.*?</{0}>)(.+?)(?=<{0}|$)'.format(detltag), re.DOTALL)
    
    for x, text in enumerate(blocks):
        repl = finder.findall(text)
        if repl:
            new = text[:text.find(repl[0][0])]
            for item in repl:
                new += details_block(item[0], item[1])
            blocks[x] = new
    
    if splttag is not None:
        text = '<{}'.format(splttag).join(blocks)
    else:
        text = ''.join(blocks)
    return text

def details_block(summary, body=None, summary_class=None, body_class=None):
    if body:
        if body_class:
            txt = '<details class="%s">' % body_class
        else:
            txt = '<details>'
        if summary_class:
            txt += '<summary class="%s">' % summary_class
        else:
            txt += '<summary>'
        txt += summary
        txt += '</summary>'
        if not body.startswith('\n'):
            txt += '\n'
        txt += body
        if not body.endswith('\n'):
            txt += '\n'
        txt += '</details>\n'
    else:
        txt = summary
    return txt

def asyncmap(func, lst):
    try:
        if not multiprocessing.pool:
            raise Exception
        with multiprocessing.pool.ThreadPool(processes=len(lst)) as pool:
            new = pool.map(func, lst)
    except:
        new = map(func, lst)
    return new
