Easy integration of reStructuredText.

The :class:`ReStructuredText`class is used to control the
ReStructuredText integration to one or more Flask applications.
Depending on how you initialize the object it is usable right
away or will attach as needed to a Flask application.

There are two usage modes which work very similiar. One is binding
the instance to a very specific Flask application::

    app = Flask(name)
    rst = ReStructuredText(app)

The second possibility is to create the object once and configure the
application later to support it::

    rst = ReStructuredText()

    def create_app():
        app = Flask(__name__)
        rst.init_app(app)
        return app



