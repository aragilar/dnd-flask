#!/usr/bin/env python2

import os
import re
import helper
from flask import Flask, render_template, url_for, abort, request

app = Flask(__name__)

releasesort = helper.release_sort
filters = {}
folder = 'data/filter'
for item in os.listdir(folder):
    if item.endswith('.json'):
        filters[item[:-5]] = helper.archiver.load(os.path.join(folder, item))
del folder

@app.errorhandler(403)
def four_oh_three(e):
    filter, show = get_filter()
    
    return render_template('error.html',
        home=url_for('index', filter=filter),
        styles=[url_for('static', filename='index.css')],
        title=str(e),
        message=[
            "You don't have access to this page."
        ]
    ), 403

@app.errorhandler(404)
def four_oh_four(e):
    filter, show = get_filter()
    
    return render_template('error.html',
        home=url_for('index', filter=filter),
        styles=[url_for('static', filename='index.css')],
        title=str(e),
        message=[
            "Our gnomes couldn't find the file you were looking for...",
            "If you entered the URL manually try checking your spelling."
        ]
    ), 404

@app.errorhandler(500)
def five_hundred(e):
    filter, show = get_filter()
    
    return render_template('error.html',
        home=url_for('index', filter=filter),
        styles=[url_for('static', filename='index.css')],
        title='500: '+str(e),
        message=[
            "Whoops, looks like something went wrong!",
            "We'll try to fix this a quickly as possible."
        ]
    ), 500

def get_filter():
    filter = request.args.get('filter')
    if filter is not None and filter in filters:
        show = filters[filter]
    else:
        show = None
    return filter, show

@app.route('/')
def index():
    filter, show = get_filter()
    
    classes = [(c, url_for('class_page', classname=c, filter=filter)) for c in releasesort(helper.getclasses(show))]
    races = [(c, url_for('race_page', racename=c, filter=filter)) for c in releasesort(helper.getraces(show))]
    rules = [(c, url_for('optionalrule_page', rule=c, filter=filter)) for c in releasesort(helper.getoptionalrules(show))]
    
    if filter is not None:
        query = '?filter=' + filter
    else:
        query = ''
    
    title = 'Home'
    if show is not None:
        title = '{!s} {!s}'.format(show.get('+', filter), title)
    
    return render_template('dnd.html',
        title=title,
        styles=[url_for('static', filename='index.css')],
        filters=sorted([(filters[f].get('+', f), f) for f in filters.keys()], key=lambda a: a[0]),
        charsheet=url_for('static', filename='character_sheet.html'),
        classlink=url_for('class_home', filter=filter),
        classes=classes,
        racelink=url_for('race_home', filter=filter),
        races=races,
        optionalrules=rules,
        slug=helper.slug,
        query=query
    )

@app.route('/class/')
def class_home():
    filter, show = get_filter()
    
    subclasses = {}
    classes = helper.getclasses(show)
    for key in classes:
        subclasses[key] = releasesort(classes[key]['subclass'])
    classes = releasesort(classes)
    
    if filter is not None:
        query = '?filter=' + filter
    else:
        query = ''
        
    return render_template('dnd-subthing.html',
        home=url_for('index', filter=filter),
        styles=[url_for('static', filename='index.css')],
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
    
    if html is not None:
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=[url_for('static', filename='index.css')],
            javascript=[url_for('static', filename='nodetails.js')],
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
        subraces[key] = releasesort(races[key]['subrace'])
    races = releasesort(races)
    
    if filter is not None:
        query = '?filter=' + filter
    else:
        query = ''
        
    return render_template('dnd-subthing.html',
        home=url_for('index', filter=filter),
        styles=[url_for('static', filename='index.css')],
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
    
    if html is not None:
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=[url_for('static', filename='index.css')],
            javascript=[url_for('static', filename='nodetails.js')],
            title=racename,
            content=html
        )
    else:
        abort(404)

@app.route('/backgrounds')
def background_page():
    filter, show = get_filter()
    
    html = helper.background_page(show)
    
    if html is not None:
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=[
                url_for('static', filename='index.css'),
                url_for('static', filename='items.css')
            ],
            javascript=[url_for('static', filename='nodetails.js')],
            title='Magic Items',
            content=html
        )
    else:
        abort(404)

@app.route('/spells')
def spell_page():
    filter, show = get_filter()
    
    html = helper.spell_page(show)
    
    if html is not None:
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=[
                url_for('static', filename='index.css'),
                url_for('static', filename='items.css')
            ],
            javascript=[
                url_for('static', filename='nodetails.js'),
                url_for('static', filename='spells.js')
            ],
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
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=[
                url_for('static', filename='index.css'),
                url_for('static', filename='items.css')
            ],
            javascript=[url_for('static', filename='nodetails.js')],
            title='Feats',
            content=html
        )
    else:
        abort(404)

@app.route('/magicitems')
def magicitem_page():
    filter, show = get_filter()
    
    html = helper.magicitem_page(show)
    
    if html is not None:
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=[
                url_for('static', filename='index.css'),
                url_for('static', filename='items.css')
            ],
            javascript=[
                url_for('static', filename='nodetails.js'),
                url_for('static', filename='magicitems.js')
            ],
            title='Magic Items',
            content=html
        )
    else:
        abort(404)

@app.route('/items')
def item_page():
    filter, show = get_filter()
    
    html = helper.item_page(show)
    
    if html is not None:
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=[
                url_for('static', filename='index.css'),
                url_for('static', filename='items.css')
            ],
            javascript=[url_for('static', filename='nodetails.js')],
            title='Items',
            content=html
        )
    else:
        abort(404)

@app.route('/documentation/<document>')
def document_page(document):
    filter, show = get_filter()
    
    html = helper.documentation(document)
    
    if html is not None:
        title = re.findall('<h1.*?>(.*?)</h1>', html)
        if len(title):
            title = title[0]
        else:
            title = document
        
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=[
                url_for('static', filename='index.css'),
                url_for('static', filename='items.css')
            ],
            javascript=[url_for('static', filename='nodetails.js')],
            title=title,
            content=html
        )
    else:
        abort(404)

@app.route('/optionalrule/<rule>')
def optionalrule_page(rule):
    filter, show = get_filter()
    
    html = helper.optionalrule_page(rule, show)
    
    if html is not None:
        title = rule
        return render_template('display.html',
            home=url_for('index', filter=filter),
            collapse_details=True,
            styles=[
                url_for('static', filename='index.css'),
                url_for('static', filename='items.css')
            ],
            javascript=[url_for('static', filename='nodetails.js')],
            title=title,
            content=html
        )
    else:
        abort(404)

if __name__ == '__main__':
    host = '127.0.0.1'
    port = int(helper.os.environ.get('PORT', 5000))
    if port != 5000:
        host = '0.0.0.0'
    print 'safari-http://%s:%d' % (host, port)
    app.run(host=host, port=port)#, debug=True, use_reloader=False)
