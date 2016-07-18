import sys
import os
import re
import traceback

from flask import Flask, render_template, url_for, abort, request, send_from_directory

import helper

app = Flask(__name__)

filters = helper.collections.OrderedDict()
everystyle = [
    '@normalize.css',
    '@index.css'
]
everyjs = [
    'https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js',
    '@accordion.js'
]
filterkey = 'name'

def init():
    global filters, started
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        args = (sys.argv[1],)
    else:
        args = ()
    helper.init(*args)
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
    
    classes = helper.class_list.filter(show).keys()
    races = helper.race_list.filter(show).keys()
    rules = helper.optionalrule_list.filter(show).keys()
    
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
        backgrounds=bool(helper.background_list.filter(show)),
        spells=bool(helper.spell_list.filter(show)),
        feats=bool(helper.feat_list.filter(show)),
        boons=bool(helper.epicboon_list.filter(show)),
        items=helper.weapon_list.filter(show) or helper.armor_list.filter(show) or helper.item_list.filter(show),
        magicitems=bool(helper.magicitem_list.filter(show)),
        documentation=documents
    )

@app.route('/character_sheet/', defaults={'look':'standard'})
@app.route('/character_sheet/<look>')
def character_sheet(look):
    filter, show = get_filter()

    if look in ['index', 'index.htm', 'index.html']:
        look = 'standard'
    
    return render_template('character_sheet.html',
        look=helper.slug(look)
    )

@app.route('/class/', defaults={'name':None})
@app.route('/class/<name>')
def class_page(name):
    filter, show = get_filter()
    
    if name is not None:
        html = helper.class2html(name, show)
        if html:
            return render_template('dnd-base.html',
                home=True,
                collapse_details=True,
                styles=everystyle,
                javascript=everyjs,
                title=name,
                content=html
            )
        else:
            abort(404)
    else:
        subclasses = {}
        classes = helper.class_list.filter(show)
        for key in classes.keys():
            subclasses[key] = classes[key].children.keys()
        classes = classes.keys()
            
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

@app.route('/race/', defaults={'name':None})
@app.route('/race/<name>')
def race_page(name):
    filter, show = get_filter()
    
    if name is not None:
        html = helper.race2html(name, show)
        
        if html:
            return render_template('dnd-base.html',
                home=True,
                collapse_details=True,
                styles=everystyle,
                javascript=everyjs,
                title=name,
                content=html
            )
        else:
            abort(404)
    else:
        subraces = {}
        races = helper.race_list.filter(show)
        for key in races.keys():
            subraces[key] = races[key].children.keys()
        races = races.keys()
        
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

@app.route('/backgrounds')
def background_page():
    filter, show = get_filter()
    
    html = helper.background_page(show)
    
    if html:
        return render_template('dnd-base.html',
            home=True,
            collapse_details=True,
            styles=everystyle,
            javascript=everyjs,
            title='Backgrounds',
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
        return render_template('dnd-base.html',
            home=True,
            collapse_details=True,
            styles=everystyle,
            javascript=everyjs,
            title='Feats',
            content=html
        )
    else:
        abort(404)

@app.route('/spells/', defaults={'name':None})
@app.route('/spells/<name>')
def spell_page(name):
    filter, show = get_filter()

    js = everyjs
    if name is None:
        html = helper.spell_page(show)
        name = 'Spells'
        js += ['@spells.js']
    else:
        html = helper.spell2html(name, show)

    if html:
        return render_template('dnd-base.html',
            home=True,
            collapse_details=True,
            styles=everystyle,
            javascript=js,
            title=name,
            content=html
        )
    else:
        abort(404)

@app.route('/magicitems/', defaults={'name':None})
@app.route('/magicitems/<name>')
def magicitem_page(name):
    filter, show = get_filter()
    
    js = everyjs
    if name is None:
        html = helper.magicitem_page(show)
        name = 'Magic Items'
        js += ['@magicitems.js']
    else:
        html = helper.magicitem2html(name, show)

    if html:
        return render_template('dnd-base.html',
            home=True,
            collapse_details=True,
            styles=everystyle,
            javascript=js,
            title=name,
            content=html
        )
    else:
        abort(404)

@app.route('/items')
def item_page():
    filter, show = get_filter()
    
    html = helper.item_page(show)
    
    if html:
        return render_template('dnd-base.html',
            home=True,
            collapse_details=True,
            styles=everystyle,
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
        
        return render_template('dnd-base.html',
            home=True,
            collapse_details=True,
            styles=everystyle,
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
        
        return render_template('dnd-base.html',
            home=True,
            collapse_details=True,
            styles=everystyle,
            javascript=everyjs,
            title=title,
            content=html
        )
    else:
        abort(404)

if __name__ == '__main__':
    # ----#-   Main
    init()
    
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
