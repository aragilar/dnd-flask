'''A module for saving and reading json'''

import json
try:
    import cStringIO as StringIO
except ImportError:
    try:
        import StringIO
    except ImportError:
        import io as StringIO

def save(object, filename, compact = False):
    '''Save object: object to file: filename,
    using the json protocol'''

    try:
        with open(filename, 'r') as f:
            text = f.read()
    except IOError:
        text = ''
    
    new = p(object, compact=compact)

    if new != text:
        with open(filename, 'w') as f:
            f.write(new)

def load(filename, debug = True):
    '''Loads a json object from file: filename'''
    try:
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
            except ValueError:
                if debug:
                    raise
                else:
                    data = None
        return data
    except IOError:
        if debug:
            raise
        else:
            return None

def p(data, compact = False):
    s = StringIO.StringIO()

    if compact:
        indent = None
        sort = False
        separators = (',', ':')
    else:
        indent = 4
        sort = True
        separators = (',', ': ')

    json.dump(data, s, indent = indent, sort_keys = sort, separators = separators)

    return s.getvalue()
