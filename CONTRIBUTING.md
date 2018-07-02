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

- MacOS or Linux
- Python 2.7

    Using 2.7 ensures that you don't accidentally break Python2.7 support.
    Flask-PyMongo will support Python 2.7 for as long as it is an officially
    supported version of Python (util some time in 2020).

- Run tests with [tox](https://tox.readthedocs.io/en/latest/), eg `tox -e
  pymongo30-mongo32-flask0_11`

    Since the build matrix is very big, you may want to select a single
    or a few matrix versions to test. Run `tox -l` to see all the builds.

    All tests, against all supported versions, are run by
    [Travis-CI](https://travis-ci.org/dcrosta/flask-pymongo) for each commit
    and pull request.

- Check style compliance with `tox -e style`


## Building the docs

Build the docs in the `docs` directory using Sphinx:

    cd docs
    make html

Open `_build/html/index.html` in your browser to view the docs.
