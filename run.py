import sys
import os
import re
import traceback
import threading
import helper
from flask import Flask, render_template, url_for, abort, request, send_from_directory

app = Flask(__name__)

filters = {}
everystyle = ['@normalize.css', '@index.css']
everyjs = ['@nodetails.js']
itemcss = '@items.css'
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
                filters[item[:-5]] = helper.archiver.load(os.path.join(folder, item))
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
    filter, show = get_filter()
    
    styles = [url_for('static', filename=file) for file in everystyle]
    js = [url_for('static', filename=file) for file in everyjs]
    
    return render_template('error.html',
        home=url_for('index', filter=filter),
        styles=styles,
        javascript=js,
        title=str(e),
        message=[
            "You don't have access to this page."
        ]
    ), 403

@app.errorhandler(404)
def four_oh_four(e):
    filter, show = get_filter()
    
    styles = [url_for('static', filename=file) for file in everystyle]
    js = [url_for('static', filename=file) for file in everyjs]
    
    return render_template('error.html',
        home=url_for('index', filter=filter),
        styles=styles,
        javascript=js,
        title=str(e),
        reload=not started,
        message=[
            "Our gnomes couldn't find the file you were looking for...",
            "If you entered the URL manually try checking your spelling."
        ]
    ), 404

@app.errorhandler(500)
def five_hundred(e):
    sys.stderr.write(traceback.format_exc())
    filter, show = get_filter()
    
    styles = [url_for('static', filename=file) for file in everystyle]
    js = [url_for('static', filename=file) for file in everyjs]
    
    return render_template('error.html',
        home=url_for('index', filter=filter),
        styles=styles,
        javascript=js,
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
    
    classes = [(c, url_for('class_page', classname=c, filter=filter)) for c in helper.getclasses(show)]
    races = [(c, url_for('race_page', racename=c, filter=filter)) for c in helper.getraces(show)]
    rules = [(c, url_for('optionalrule_page', rule=c, filter=filter)) for c in helper.getoptionalrules(show)]
    
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
        title = '{!s} {!s}'.format(show.get('+', filter), title)
    
    return render_template('dnd.html',
        title=title,
        styles=everystyle,
        javascript=everyjs,
        filters=sorted([(filters[f].get('+', f), f) for f in filters.keys()], key=lambda a: a[0]),
        optionalrules=rules,
        slug=helper.slug,
        query=query,
        
        classlink=url_for('class_home', filter=filter),
        classes=classes,
        racelink=url_for('race_home', filter=filter),
        races=races,
        backgrounds=bool(helper.getbackgrounds(show)),
        spells=bool(helper.getspells(show)),
        feats=bool(helper.getfeats(show)),
        boons=bool(helper.getepicboons(show)),
        items=helper.getweapons(show) or helper.getarmors(show) or helper.getitems(show),
        magicitems=bool(helper.getmagicitems(show)),
        documentation=documents
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
        home=url_for('index', filter=filter),
        styles=everystyle,
        javascript=everyjs,
        name='Classes',
        things=classes,
        subthings=subclasses,
        slug=helper.slug,
        query=query
    )

@app.route('/class/<classname>')
def class_page(classname):
    filter, show = get_filter()
    
    html = helper.class2html(classname, show)
    
    if html:
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=everystyle,
            javascript=everyjs,
            title=classname,
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
        home=url_for('index', filter=filter),
        styles=everystyle,
        javascript=everyjs,
        name='Races',
        things=races,
        subthings=subraces,
        slug=helper.slug,
        query=query
    )

@app.route('/race/<racename>')
def race_page(racename):
    filter, show = get_filter()
    
    html = helper.race2html(racename, show)
    
    if html:
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=everystyle,
            javascript=everyjs,
            title=racename,
            content=html
        )
    else:
        abort(404)

@app.route('/backgrounds')
def background_page():
    filter, show = get_filter()
    
    html = helper.background_page(show)
    
    if html:
        styles = everystyle[:]
        styles.append(itemcss)
        
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=styles,
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
        styles = everystyle[:]
        styles.append(itemcss)
        js = everyjs[:]
        js.append('@spells.js')
        
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=styles,
            javascript=js,
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
        styles = everystyle[:]
        styles.append(itemcss)
        
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=styles,
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
        styles = everystyle[:]
        styles.append(itemcss)
        js = everyjs[:]
        js.append('@magicitems.js')
        
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=styles,
            javascript=js,
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
        styles = everystyle[:]
        styles.append(itemcss)
        
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=styles,
            javascript=everyjs,
            title='Items',
            content=html
        )
    else:
        abort(404)

@app.route('/documentation/<document>')
def document_page(document):
    filter, show = get_filter()
    
    html = helper.documentation(document)
    
    if html:
        title = re.findall('<h1.*?>(.*?)</h1>', html)
        if len(title):
            title = title[0]
        else:
            title = document
        
        styles = everystyle[:]
        styles.append(itemcss)
        
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=styles,
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
        
        styles = everystyle[:]
        styles.append(itemcss)
        
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=styles,
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
        print('safari-http://%s:%d' % (host, port))
    
    app.run(host=host, port=port, debug=debug, use_reloader=False)
    
    t.join()
