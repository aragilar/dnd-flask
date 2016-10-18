#!/usr/bin/env python3

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

everystyle = [
    '/static/normalize.css',
    '/static/index.css'
]
everyjs = [
    '/static/jquery.min.js',
    '/static/accordion.js',
    '/static/keep-params.js'
]

def get_filter():
    filter_name = request.args.get('filter')
    if filter_name not in helper.filter_list.keys():
        filter_name = None
    return filter_name

def error(e, message):
    html = render_template('error.html',
        home=True,
        styles=everystyle,
        javascript=everyjs,
        title=str(e),
        message=message,
    )

    return html

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
    filter_name = get_filter()

    if look in ['index', 'index.htm', 'index.html']:
        look = 'standard'
    look = helper.slug(look)

    html = render_template('character_sheet.html',
        look=look,
        styles=[
            '/static/normalize.css',
            '/static/character_sheet/character_sheet.css',
            '/static/character_sheet/%s.css' % look
        ],
        javascript=everyjs+["/static/character_sheet/character_sheet.js"],
    )

    return html

@app.route('/')
def index():
    filter_name = get_filter()

    title = 'Home'
    if filter_name is not None:
        title = '{} {}'.format(
            filter_name,
            title
        )

    data = {
        'classes': helper.class_list.filter(filter_name),
        'races': helper.race_list.filter(filter_name),
        'backgrounds': helper.background_list.filter(filter_name),
        'spells': helper.spell_list.filter(filter_name),
        'feats': helper.feat_list.filter(filter_name),
        'boons': helper.epicboon_list.filter(filter_name),
        'items': (
            list(helper.weapon_list.filter(filter_name))
            + list(helper.armor_list.filter(filter_name))
            + list(helper.item_list.filter(filter_name))
        ),
        'monsters': helper.monster_list.filter(filter_name),
        'magicitems': helper.magicitem_list.filter(filter_name),
        'documentation': helper.document_list.filter(filter_name),
        'optionalrules': helper.optionalrule_list.filter(filter_name),
    }

    html = render_template('dnd.html',
        title=title,
        styles=everystyle,
        javascript=everyjs+['/static/filters.js'],
        filters=helper.filter_list.keys(),
        slug=helper.slug,
        **data
    )

    return html

@app.route('/classes/', defaults={'type':'Classes'})
@app.route('/races/', defaults={'type':'Races'})
def subpage(type):
    filter_name = get_filter()

    data = {
        'Classes': helper.class_list,
        'Races': helper.race_list,
    }.get(type)

    if not data:
        return abort(404)

    data = data.filter(filter_name)

    html = render_template('dnd-subthing.html',
        home=True,
        styles=everystyle,
        javascript=everyjs,
        name=type,
        things=data,
        slug=helper.slug,
    )

    if not html:
        return abort(404)

    return html

@app.route('/classes/<name>', defaults={'type':'Classes'})
@app.route('/races/<name>', defaults={'type':'Races'})
@app.route('/spells/<name>', defaults={'type':'Spells'})
@app.route('/monsters/<name>', defaults={'type':'Monsters'})
@app.route('/magicitems/<name>', defaults={'type':'Magic Items'})
@app.route('/documentation/<name>', defaults={'type':'Documentation'})
@app.route('/optionalrule/<name>', defaults={'type':'Optional Rules'})
def subthing(name, type):
    filter_name = get_filter()

    type = {
        'Classes': helper.class_list,
        'Races': helper.race_list,
        'Spells': helper.spell_list,
        'Monsters': helper.monster_list,
        'Magic Items': helper.magicitem_list,
        'Documentation': helper.document_list,
        'Optional Rules': helper.optionalrule_list,
    }.get(type)

    if not type:
        return abort(404)

    type = type.filter(filter_name)

    if name in type:
        item = type[name]
        html = item.page()
        name = item.name
    else:
        html = None

    if html:
        html = render_template('dnd-base.html',
            home=True,
            collapse_details=True,
            styles=everystyle,
            javascript=everyjs,
            title=name,
            content=html,
        )

    if not html:
        return abort(404)

    return html

@app.route('/backgrounds', defaults={'type':'Backgrounds'})
@app.route('/feats', defaults={'type':'Feats'})
@app.route('/items', defaults={'type':'Items'})
@app.route('/spells/', defaults={'type':'Spells'})
@app.route('/monsters/', defaults={'type':'Monsters'})
@app.route('/magicitems/', defaults={'type':'Magic Items'})
def list_page(type):
    filter_name = get_filter()

    data = {
        'Spells': [
            helper.spell_list,
        ],
        'Monsters': [
            helper.monster_list,
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
        item = item.filter(filter_name)
        if item:
            if hasattr(item, 'javascript'):
                js += ['/static/' + a for a in item.javascript]
            page = item.page()
            html += page

    if not html:
        return abort(404)

    html = render_template('dnd-base.html',
        home=True,
        collapse_details=True,
        styles=style,
        javascript=js,
        title=type,
        content=html,
    )

    return html

@app.route('/monsters/groups/', defaults={'type':'Monsters'})
def groups_page(type):
    filter_name = get_filter()

    data = {
        'Monsters': helper.monster_list,
    }.get(type)

    if not data:
        return abort(404)

    data = data.filter(filter_name)
    if data:
        html = data.groups_page()
    else:
        html = None

    if not html:
        return abort(404)

    html = render_template('dnd-base.html',
        home=True,
        collapse_details=True,
        styles=everystyle,
        javascript=everyjs,
        title='Groups (%s)' % type,
        content=html,
    )

    return html

if __name__ == '__main__':
    import argparse
    # ----#-   Main
    parser = argparse.ArgumentParser(description="D&D web server", epilog="The server runs locally on port 5000 if PORT is not specified.")
    parser.add_argument("-f", dest="file", help="The location of the database file")
    parser.add_argument("-p", dest="port", help="The port where the server will run")
    args = parser.parse_args()
    helper.init(args.file)

    if args.port is not None: # Public System
        port = int(args.port)
        host = '0.0.0.0'
        debug = False
    else: # Private System
        port = 5000
        host = '127.0.0.1'
        debug = False

        print('safari-http://%s:%d/' % (host, port))

    app.run(host=host, port=port, debug=debug, use_reloader=False)
