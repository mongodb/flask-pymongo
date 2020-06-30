# Flask-PyMongo

PyMongo support for Flask applications

## Quickstart

```python
from flask import Flask, render_template
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)

@app.route('/')
def home_page():
    online_users = mongo.db.users.find({'online': True})
    return render_template('index.html', online_users=online_users)
```

## More Info

* [Flask-PyMongo Documentation](https://flask-pymongo.readthedocs.org/)
* [PyMongo Documentation](https://pymongo.readthedocs.io/en/stable/)
* [Flask Documentation](https://flask.palletsprojects.com/)
