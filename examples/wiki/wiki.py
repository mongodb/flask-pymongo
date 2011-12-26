from flask import Flask, redirect, render_template, request, url_for
from flask.ext.pymongo import PyMongo
import markdown2
import re

app = Flask(__name__)
mongo = PyMongo(app)

WIKIPART = re.compile(r'([A-Z][a-z0-9_]+)')
WIKIWORD = re.compile(r'([A-Z][a-z0-9_]+(?:[A-Z][a-z0-9_]+)+)')

@app.template_filter()
def totitle(value):
    return ' '.join(WIKIPART.findall(value))

@app.template_filter()
def wikify(value):
    parts = WIKIWORD.split(value)
    for i, part in enumerate(parts):
        if WIKIWORD.match(part):
            name = totitle(part)
            parts[i] = '[%s](%s)' % (name, url_for('show_page', pagepath=part))
    return markdown2.markdown(''.join(parts))

@app.route('/<path:pagepath>')
def show_page(pagepath):
    page = mongo.db.pages.find_one_or_404({'_id': pagepath})
    return render_template('page.html',
        page=page,
        pagepath=pagepath)

app.add_url_rule('/', 'homepage_redirect', redirect_to='/HomePage')

@app.route('/edit/<path:pagepath>', methods=['GET'])
def edit_page(pagepath):
    page = mongo.db.pages.find_one_or_404({'_id': pagepath})
    return render_template('edit.html',
        page=page,
        pagepath=pagepath)

@app.route('/edit/<path:pagepath>', methods=['POST'])
def save_page(pagepath):
    if 'cancel' not in request.form:
        mongo.db.pages.update(
            {'_id': pagepath},
            {'$set': {'body': request.form['body']}},
            safe=True, upsert=True)
    return redirect(url_for('show_page', pagepath=pagepath))

@app.errorhandler(404)
def new_page(error):
    pagepath = request.path.lstrip('/') or 'HomePage'
    return render_template('edit.html', page=None, pagepath=pagepath)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
    app.run(debug=True)

