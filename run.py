import sys
import os
import re
import traceback
import threading
import helper
from flask import Flask, render_template, url_for, abort, request, send_from_directory

app = Flask(__name__)

filters = helper.collections.OrderedDict()
everystyle = ['@normalize.css', '@index.css']
everyjs = ['@nodetails.js']
itemcss = '@items.css'
filterkey = 'name'
started = False

def init():
    global filters, started
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        args = (sys.argv[1],)
    else:
        args = ()
    t = threading.Thread(target=helper.init, args=args)
    t.start()
    folder = os.path.join(helper.datafolder, 'filter')
    if os.path.exists(folder):
        for item in os.listdir(folder):
            if item.endswith('.json'):
                d = helper.archiver.load(os.path.join(folder, item))
                if filterkey not in d:
                    d[filterkey] = item[:-5]
                filters[d[filterkey]] = d
        for key in sorted(filters):
            try:
                filters.move_to_end(key)
            except AttributeError:
                d = filters[key]
                del filters[key]
                filters[key] = d
    t.join()
    started = True

def get_filter():
    filter = request.args.get('filter')
    if filter is not None and filter in filters:
        show = filters[filter]
    else:
        show = None
    return filter, show

@app.errorhandler(403)
def four_oh_three(e):
    return render_template('error.html',
        home=True,
        styles=everystyle,
        javascript=everyjs,
        title=str(e),
        message=[
            "You don't have access to this page."
        ]
    ), 403

@app.errorhandler(404)
def four_oh_four(e):
    return render_template('error.html',
        home=True,
        styles=everystyle,
        javascript=everyjs,
        title=str(e),
        #reload=not started,
        message=[
            "Our gnomes couldn't find the file you were looking for...",
            "If you entered the URL manually try checking your spelling."
        ]
    ), 404

@app.errorhandler(500)
def five_hundred(e):
    sys.stderr.write(traceback.format_exc())
    
    return render_template('error.html',
        home=True,
        styles=everystyle,
        javascript=everyjs,
        title='500: '+str(e),
        message=[
            "Whoops, looks like something went wrong!",
            "We'll try to fix this a quickly as possible."
        ]
    ), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'images'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/')
def index():
    filter, show = get_filter()
    
    classes = helper.getclasses(show).keys()
    races = helper.getraces(show).keys()
    rules = helper.getoptionalrules(show).keys()
    
    if helper.datafolder is not None:
        documents = os.path.exists(os.path.join(helper.datafolder, 'documentation'))
    else:
        documents = False
    
    if filter is not None:
        query = '?filter=' + filter
    else:
        query = ''
    
    title = 'Home'
    if show is not None:
        title = '{!s} {!s}'.format(show.get(filterkey, filter), title)
    
    return render_template('dnd.html',
        title=title,
        styles=everystyle,
        javascript=everyjs+['@filters.js'],
        filters=filters.keys(),
        optionalrules=rules,
        slug=helper.slug,
        
        classes=classes,
        races=races,
        backgrounds=bool(helper.getbackgrounds(show)),
        spells=bool(helper.getspells(show)),
        feats=bool(helper.getfeats(show)),
        boons=bool(helper.getepicboons(show)),
        items=helper.getweapons(show) or helper.getarmors(show) or helper.getitems(show),
        magicitems=bool(helper.getmagicitems(show)),
        documentation=documents
    )

@app.route('/character_sheet/', defaults={'look': 'standard'})
@app.route('/character_sheet/<look>')
def character_sheet(look):
    filter, show = get_filter()

    if look in ['index', 'index.htm', 'index.html']:
        look = 'standard'
    
    return render_template('character_sheet.html',
        look=look,
        slug=helper.slug
    )

@app.route('/class/')
def class_home():
    filter, show = get_filter()
    
    subclasses = {}
    classes = helper.getclasses(show)
    for key in classes:
        subclasses[key] = classes[key]['subclass'].keys()
    classes = classes.keys()
    
    if filter is not None:
        query = '?filter=' + filter
    else:
        query = ''
        
    return render_template('dnd-subthing.html',
        home=True,
        styles=everystyle,
        javascript=everyjs,
        name='Classes',
        subpage='class_page',
        things=classes,
        subthings=subclasses,
        slug=helper.slug
    )

@app.route('/class/<name>')
def class_page(name):
    filter, show = get_filter()
    
    html = helper.class2html(name, show)
    
    if html:
        return render_template('display.html',
            home=True,
            collapse_details=True,
            styles=everystyle,
            javascript=everyjs,
            title=name,
            content=html
        )
    else:
        abort(404)

@app.route('/race/')
def race_home():
    filter, show = get_filter()
    
    subraces = {}
    races = helper.getraces(show)
    for key in races:
        subraces[key] = races[key]['subrace'].keys()
    races = races.keys()
    
    if filter is not None:
        query = '?filter=' + filter
    else:
        query = ''
    
    return render_template('dnd-subthing.html',
        home=True,
        styles=everystyle,
        javascript=everyjs,
        name='Races',
        subpage='race_page',
        things=races,
        subthings=subraces,
        slug=helper.slug
    )

@app.route('/race/<name>')
def race_page(name):
    filter, show = get_filter()
    
    html = helper.race2html(name, show)
    
    if html:
        return render_template('display.html',
            home=True,
            collapse_details=True,
            styles=everystyle,
            javascript=everyjs,
            title=name,
            content=html
        )
    else:
        abort(404)

@app.route('/backgrounds')
def background_page():
    filter, show = get_filter()
    
    html = helper.background_page(show)
    
    if html:
        return render_template('display.html',
            home=True,
            collapse_details=True,
            styles=everystyle+[itemcss],
            javascript=everyjs,
            title='Backgrounds',
            content=html
        )
    else:
        abort(404)

@app.route('/spells')
def spell_page():
    filter, show = get_filter()
    
    html = helper.spell_page(show)
    
    if html:
        return render_template('display.html',
            home=True,
            collapse_details=True,
            styles=everystyle+[itemcss],
            javascript=everyjs+['@spells.js'],
            title='Spells',
            content=html
        )
    else:
        abort(404)

@app.route('/feats')
def feat_page():
    filter, show = get_filter()
    
    feats = helper.feat_page(show)
    boons = helper.boon_page(show)
    
    if feats is None:
        feats = ''
    
    if boons is None:
        boons = ''
    
    html = feats + boons
    
    if html:
        return render_template('display.html',
            home=True,
            collapse_details=True,
            styles=everystyle+[itemcss],
            javascript=everyjs,
            title='Feats',
            content=html
        )
    else:
        abort(404)

@app.route('/magicitems')
def magicitem_page():
    filter, show = get_filter()
    
    html = helper.magicitem_page(show)
    
    if html:
        return render_template('display.html',
            home=True,
            collapse_details=True,
            styles=everystyle+[itemcss],
            javascript=everyjs+['@magicitems.js'],
            title='Magic Items',
            content=html
        )
    else:
        abort(404)

@app.route('/items')
def item_page():
    filter, show = get_filter()
    
    html = helper.item_page(show)
    
    if html:
        return render_template('display.html',
            home=True,
            collapse_details=True,
            styles=everystyle+[itemcss],
            javascript=everyjs,
            title='Items',
            content=html
        )
    else:
        abort(404)

@app.route('/documentation/<document>')
def document_page(document):
    html = helper.documentation(document)
    
    if html:
        title = re.findall('<h1.*?>(.*?)</h1>', html)
        if len(title):
            title = title[0]
        else:
            title = document
        
        return render_template('display.html',
            home=True,
            collapse_details=True,
            styles=everystyle+[itemcss],
            javascript=everyjs,
            title=title,
            content=html
        )
    else:
        abort(404)

@app.route('/optionalrule/<rule>')
def optionalrule_page(rule):
    filter, show = get_filter()
    
    html = helper.optionalrule_page(rule, show)
    
    if html:
        title = rule
        
        return render_template('display.html',
            home=True,
            collapse_details=True,
            styles=everystyle+[itemcss],
            javascript=everyjs,
            title=title,
            content=html
        )
    else:
        abort(404)

if __name__ == '__main__':
    t = threading.Thread(target=init)
    t.start()
    
    if 'PORT' in os.environ: # Public System
        port = int(os.environ['PORT'])
        host = '0.0.0.0'
        debug = False
    else: # Private System
        port = 5000
        host = '127.0.0.1'
        debug = False
        print('safari-http://%s:%d/' % (host, port))
    
    app.run(host=host, port=port, debug=debug, use_reloader=False)
    
    t.join()
