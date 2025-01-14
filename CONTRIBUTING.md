# How to contribute to Flask-PyMongo

Thank you for considering contributing to Flask-PyMongo!


## Support questions

For help and general questions, please consider using the [flask-pymongo
tag](https://stackoverflow.com/questions/tagged/flask-pymongo) on
[StackOverflow](https://stackoverflow.com/) instead of creating issues in
the GitHub project. This will keep the issues in the project focused on
actual bugs and improvement requests.


## Reporting issues

- Describe what you expected to happen.
- If possible, include a [minimal, complete, and verifiable
  example](https://stackoverflow.com/help/mcve) to help us identify the issue.
  This also helps check that the issue is not with your own code.
- Describe what actually happened. Include the full traceback if there was an
  exception.
- List your Flask-PyMongo, PyMongo, and MongoDB versions. If possible, check if
  this issue is already fixed in the repository.


## Submitting patches

- All new features must include a test. Flask-PyMongo is tested against a
  matrix of all supported versions of Flask, PyMongo, and MongoDB, so tests
  ensure that your change works for all users.
- There is also a `style` build. Please ensure your code conforms to
  Flask-PyMongo's style rules with `tox -e style`
- Use [Sphinx](http://www.sphinx-doc.org/en/master/)-style docstrings


## Recommended development environment

We use [justfile](https://just.systems/man/en/packages.html) for task running
and [uv](https://docs.astral.sh/uv/getting-started/installation/) for python project management.

To set up your dev environment, run `just install`.

To run the tests, run `just test`.  You can pass arguments through to `pytest`.

To run the linters, run `just lint`.

To build the docs, run `just docs` and  open `_build/html/index.html` in your browser to view the docs.


## Contributors

- [jeverling](https://github.com/jeverling)
- [tang0th](https://github.com/tang0th)
- [Fabrice Aneche](https://github.com/akhenakh)
- [Thor Adam](https://github.com/thoradam)
- [Christoph Herr](https://github.com/jarus)
- [Mark Unsworth](https://github.com/markunsworth)
- [Kevin Funk](https://github.com/k-funk)
- [Ben Jeffrey](https://github.com/jeffbr13)
- [Emmanuel Valette](https://github.com/karec)
- [David Awad](https://github.com/DavidAwad)
- [Robson Roberto Souza Peixoto](https://github.com/robsonpeixoto)
- [juliascript](https://github.com/juliascript)
- [Henrik Blidh](https://github.com/hbldh)
- [jobou](https://github.com/jbouzekri)
- [Craig Davis](https://github.com/blade2005)
- [ratson](https://github.com/ratson)
- [Abraham Toriz Cruz](https://github.com/categulario)
- [MinJae Kwon](https://github.com/mingrammer)
- [yarobob](https://github.com/yarobob)
- [Andrew C. Hawkins](https://github.com/achawkins)
- [Steven Silvester](https://github.com/blink1073)
