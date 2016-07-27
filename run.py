import sys
import os
import re
import logging

from flask import Flask, render_template, url_for, abort, request, send_from_directory

import helper

app = Flask(__name__)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

log = logging.getLogger('FlaskApp')
log.setLevel(logging.ERROR)
app.logger.addHandler(log)

filters = helper.collections.OrderedDict()
everystyle = [
    '@normalize.css',
    '@index.css'
]
everyjs = [
    '@jquery.min.js',
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

def final_pass(html):
    items = re.findall('="@(.+?)"', html)
    for item in items:
        html = html.replace(
            '="@%s"' % item,
            '="%s"' % url_for('static', filename=item)
        )
    return html

def error(e, message):
    html = render_template('error.html',
        home=True,
        styles=everystyle,
        javascript=everyjs,
        title=str(e),
        message=message,
    )
    
    return final_pass(html)

@app.errorhandler(403)
def four_oh_three(e):
    error(e, [
        "You don't have access to this page."
    ]), 403

@app.errorhandler(404)
def four_oh_four(e):
    return error(e, [
        "Our gnomes couldn't find the file you were looking for...",
        "If you entered the URL manually try checking your spelling.",
    ]), 404

@app.errorhandler(500)
def five_hundred(e):
    return error('500: '+str(e), [
        "Whoops, looks like something went wrong!",
        "We'll try to fix this a quickly as possible."
    ]), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'images'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon',
    )

@app.route('/character_sheet/', defaults={'look':'standard'})
@app.route('/character_sheet/<look>')
def character_sheet(look):
    filter, show = get_filter()

    if look in ['index', 'index.htm', 'index.html']:
        look = 'standard'
    
    html = render_template('character_sheet.html',
        look=helper.slug(look)
    )
    
    return final_pass(html)

@app.route('/')
def index():
    filter, show = get_filter()
    
    title = 'Home'
    if show is not None:
        title = '{} {}'.format(
            show.get(filterkey, filter),
            title
        )
    
    html = render_template('dnd.html',
        title=title,
        styles=everystyle,
        javascript=everyjs+['@filters.js'],
        filters=filters.keys(),
        slug=helper.slug,
        
        classes=helper.class_list.filter(show).keys(),
        races=helper.race_list.filter(show).keys(),
        backgrounds=bool(helper.background_list.filter(show)),
        spells=bool(helper.spell_list.filter(show)),
        feats=bool(helper.feat_list.filter(show)),
        boons=bool(helper.epicboon_list.filter(show)),
        items=helper.weapon_list.filter(show) or helper.armor_list.filter(show) or helper.item_list.filter(show),
        magicitems=bool(helper.magicitem_list.filter(show)),
        documentation=helper.document_list.filter(show).keys(),
        optionalrules=helper.optionalrule_list.filter(show).keys(),
    )
    
    return final_pass(html)

@app.route('/class/', defaults={'type':'Classes'})
@app.route('/race/', defaults={'type':'Races'})
def subpage(type):
    filter, show = get_filter()
    
    data = {
        'Classes': helper.class_list,
        'Races': helper.race_list,
    }.get(type)
    
    if not data:
        return abort(404)
    
    data = data.filter(show)
    
    html = render_template('dnd-subthing.html',
        home=True,
        styles=everystyle,
        javascript=everyjs,
        name=type,
        things=data,
        slug=helper.slug
    )
    
    if not html:
        return abort(404)
    
    return final_pass(html)

@app.route('/class/<name>', defaults={'type':'Classes'})
@app.route('/race/<name>', defaults={'type':'Races'})
@app.route('/spells/<name>', defaults={'type':'Spells'})
@app.route('/magicitems/<name>', defaults={'type':'Magic Items'})
@app.route('/documentation/<name>', defaults={'type':'Documentation'})
@app.route('/optionalrule/<name>', defaults={'type':'Optional Rules'})
def subthing(name, type):
    filter, show = get_filter()
    
    type = {
        'Classes': helper.class_list,
        'Races': helper.race_list,
        'Spells': helper.spell_list,
        'Magic Items': helper.magicitem_list,
        'Documentation': helper.document_list,
        'Optional Rules': helper.optionalrule_list,
    }.get(type)
    
    if not type:
        return abort(404)
    
    type = type.filter(show)
    
    if name in type:
        html = str(type[name])
    else:
        html = None
    
    if html:
        html = render_template('dnd-base.html',
            home=True,
            collapse_details=True,
            styles=everystyle,
            javascript=everyjs,
            title=name,
            content=html
        )
    
    if not html:
        return abort(404)
    
    return final_pass(html)

@app.route('/backgrounds', defaults={'type':'Backgrounds'})
@app.route('/feats', defaults={'type':'Feats'})
@app.route('/items', defaults={'type':'Items'})
@app.route('/spells/', defaults={'type':'Spells'})
@app.route('/magicitems/', defaults={'type':'Magic Items'})
def list_page(type):
    filter, show = get_filter()
    
    data = {
        'Spells': [
            helper.spell_list,
        ],
        'Magic Items': [
            helper.magicitem_list,
        ],
        'Backgrounds': [
            helper.background_list,
        ],
        'Feats': [
            helper.feat_list,
            helper.epicboon_list,
        ],
        'Items': [
            helper.item_list,
            helper.weapon_list,
            helper.armor_list,
        ],
    }.get(type)
    
    if not data:
        return abort(404)
    
    html = ''
    style = everystyle
    js = everyjs
    for item in data:
        item = item.filter(show)
        if item:
            if hasattr(item, 'javascript'):
                js += ['@' + a for a in item.javascript]
            html += item.page()

    if not html:
        return abort(404)
    
    html = render_template('dnd-base.html',
        home=True,
        collapse_details=True,
        styles=style,
        javascript=js,
        title=type,
        content=html
    )
    
    return final_pass(html)

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
