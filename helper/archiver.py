"""
A module for saving and loading JSON
"""

import sys
import json

class encoder (json.JSONEncoder):
    """
    A JSON encoder with compact and non-compact views
    """
    def __init__(self, compact=False, **kwargs):
        """
        Calls to JSONEncoder's __init__
        with some values overwritten based on compactness
        
        value      | compact    | not
        indent     | None       | 4
        sort_keys  | False      | True
        separators | (',', ':') | (',', ': ')
        """
        
        if compact:
            kwargs['indent'] = None
            kwargs['sort_keys'] = False
            kwargs['separators'] = (',', ':')
        else:
            kwargs['indent'] = 4
            kwargs['sort_keys'] = True
            kwargs['separators'] = (',', ': ')
        
        json.JSONEncoder.__init__(self, **kwargs)

def save(data, filename, compact=False, **kwargs):
    """
    Saves a JSON object to the given file
    """
    with open(filename, 'w') as f:
        json.dump(data, f, cls=encoder, compact=compact, **kwargs)

def load(filename, debug=True, **kwargs):
    """
    Loads a json object from the given file
    """
    try:
        with open(filename, 'r') as f:
            try:
                data = json.load(f, **kwargs)
            except (ValueError):
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

def p(data, compact=False, **kwargs):
    return json.dumps(data, cls=encoder, compact=compact, **kwargs)

if __name__ == '__main__':
    #load(sys.argv[0])
    print(p({'a': 0, 'b': 1}, compact=False))
