from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import markdown2  # type:ignore[import-untyped]
from flask import Flask, redirect, render_template, request, url_for

from flask_pymongo import PyMongo

if TYPE_CHECKING:
    from werkzeug.wrappers.response import Response

app = Flask(__name__)
mongo = PyMongo(app, "mongodb://localhost/wiki")

WIKIPART = re.compile(r"([A-Z][a-z0-9_]+)")
WIKIWORD = re.compile(r"([A-Z][a-z0-9_]+(?:[A-Z][a-z0-9_]+)+)")


@app.route("/", methods=["GET"])
def redirect_to_homepage() -> Response:
    return redirect(url_for("show_page", pagepath="HomePage"))


@app.template_filter()
def totitle(value: str) -> str:
    return " ".join(WIKIPART.findall(value))


@app.template_filter()
def wikify(value: str) -> Any:
    parts = WIKIWORD.split(value)
    for i, part in enumerate(parts):
        if WIKIWORD.match(part):
            name = totitle(part)
            url = url_for("show_page", pagepath=part)
            parts[i] = f"[{name}]({url})"
    return markdown2.markdown("".join(parts))


@app.route("/<path:pagepath>")
def show_page(pagepath: str) -> str:
    assert mongo.db is not None
    page: dict[str, Any] = mongo.db.pages.find_one_or_404({"_id": pagepath})
    return render_template("page.html", page=page, pagepath=pagepath)


@app.route("/edit/<path:pagepath>", methods=["GET"])
def edit_page(pagepath: str) -> str:
    assert mongo.db is not None
    page: dict[str, Any] = mongo.db.pages.find_one_or_404({"_id": pagepath})
    return render_template("edit.html", page=page, pagepath=pagepath)


@app.route("/edit/<path:pagepath>", methods=["POST"])
def save_page(pagepath: str) -> Response:
    if "cancel" not in request.form:
        assert mongo.db is not None
        mongo.db.pages.update(
            {"_id": pagepath},
            {"$set": {"body": request.form["body"]}},
            w=1,
            upsert=True,
        )
    return redirect(url_for("show_page", pagepath=pagepath))


@app.errorhandler(404)
def new_page(error: Any) -> str:
    pagepath = request.path.lstrip("/")
    if pagepath.startswith("uploads"):
        filename = pagepath[len("uploads") :].lstrip("/")
        return render_template("upload.html", filename=filename)
    return render_template("edit.html", page=None, pagepath=pagepath)


@app.route("/uploads/<path:filename>")
def get_upload(filename: str) -> Response:
    return mongo.send_file(filename)


@app.route("/uploads/<path:filename>", methods=["POST"])
def save_upload(filename: str) -> str | Response:
    if request.files.get("file"):
        mongo.save_file(filename, request.files["file"])
        return redirect(url_for("get_upload", filename=filename))
    return render_template("upload.html", filename=filename)


if __name__ == "__main__":
    import doctest

    doctest.testmod()
    app.run(debug=True)
