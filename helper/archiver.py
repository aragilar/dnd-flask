"""
A module for saving and reading json
"""

import sys
import json

class encoder (json.JSONEncoder):
    def __init__(self, **kwargs):
        if self.compact:
            kwargs['indent'] = None
            kwargs['sort_keys'] = False
            kwargs['separators'] = (',', ':')
        else:
            kwargs['indent'] = 4
            kwargs['sort_keys'] = True
            kwargs['separators'] = (',', ': ')
        
        json.JSONEncoder.__init__(self, **kwargs)

class cencoder (encoder):
    compact = True
class nencoder (encoder):
    compact = False

def save(data, filename, compact=False):
    """
    Saves a JSON object to the given file
    """
    if compact:
        enc = cencoder
    else:
        enc = nencoder
    with open(filename, 'w') as f:
        json.dump(data, f, cls=enc)

def load(filename, debug=True):
    """
    Loads a json object from the given file
    """
    try:
        with open(filename, 'r') as f:
            try:
                data = json.load(f)
            except ValueError:
                if debug:
                    sys.stderr.write('JSON error in file: %s\n' % filename)
                    raise
                else:
                    data = None
        return data
    except IOError:
        if debug:
            sys.stderr.write('Could not open file: %s\n' % filename)
            raise
        else:
            return None

def p(data, compact=False):
    if compact:
        enc = cencoder
    else:
        enc = nencoder
    return json.dumps(data, cls=enc)

if __name__ == '__main__':
    #load(sys.argv[0])
    print(p({'a': 0, 'b': 1}, compact=False))
