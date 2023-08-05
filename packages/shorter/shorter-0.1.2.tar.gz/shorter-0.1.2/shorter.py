import datetime
import random
import string

from flask_sqlalchemy import SQLAlchemy

from flask import (
    Flask,
    abort,
    jsonify,
    redirect,
    request,
)

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

app = Flask(__name__)
app.config.from_pyfile("shorter_config.py", silent=True)
app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///shorter.db")

db = SQLAlchemy(app)


def random_string(n):
    return ''.join(random.choice(string.ascii_letters) for x in range(n))


class Url(db.Model):
    __tablename__ = "url"

    id = db.Column(db.Integer, primary_key=True)
    short = db.Column(db.String, unique=True, nullable=False)
    full = db.Column(db.String, nullable=False)
    stats = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(
        db.DateTime(timezone=True), default=datetime.datetime.now,
        nullable=False, index=True)

    def __init__(self, url, length=6):
        self.full = url
        self.created_at = datetime.datetime.now()
        self.short = random_string(length)

    def __repr__(self):
        return "<URL('{0}' -> '{1}', count: {2})>".format(
            self.short, self.full, self.stats)


@app.before_first_request
def initialize_database():
    db.create_all()


@app.route("/")
def greeting():
    return "Welcome to url shorten service!"


@app.route("/url", methods=["POST"])
def shorten():
    def _save(url):
        for i in range(10):
            try:
                url_model = Url(url)
                db.session.add(url_model)
                db.session.commit()
                return url_model.short
            except IntegrityError as e:
                app.logger.info(e)
                db.session.rollback()
        abort(500)

    def _short(url):
        url_model = Url.query.filter(Url.full == url).first()
        return url_model.short if url_model else _save(url)

    if request.json:
        url = request.json["url"]
        return jsonify({"short": _short(url)})
    else:
        url = request.form["url"]
        return _short(url)


@app.route("/<short>")
def expand(short):
    try:
        url = Url.query.filter(Url.short == short).one()
        return redirect(url.full)
    except NoResultFound:
        abort(404)


def main():
    app.run(debug=True)


if __name__ == '__main__':
    main()
