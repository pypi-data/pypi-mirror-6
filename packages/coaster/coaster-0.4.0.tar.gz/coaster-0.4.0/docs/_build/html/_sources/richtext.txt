Rich text columns for SQLAlchemy
================================

Coaster provides a richtext column for SQLAlchemy that stores plaintext,
richtext and the name of the converting filter as a JSON-encoded dictionary.
The column defaults to Markdown (with HTML-escaping), but can be configured
to use another filter::

    from flask import Flask, Markup
    from flask.ext.sqlalchemy import SQLAlchemy
    from coaster.richtext import RichText

    app = Flask(__name__)
    db = SQLAlchemy(app)

    class MyModel(db.Model):
        __tablename__ = 'my_model'
        description = db.Column(RichText)

    model = MyModel()
    model.description = "Hello"
    assert model.description.html == Markup('<p>Hello</p>')

.. automodule:: coaster.richtext
    :members:
