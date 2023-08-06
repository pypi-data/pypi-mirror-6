"""Easy integration of reStructuredText.

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

"""
from setuptools import setup

setup(
    name='Flask-reStructuredText',
    version='1.0',
    url='http://example.com/flask-sqlite3/',
    license='BSD',
    author='Dennis Fink',
    author_email='dennis.fink@c3l.lu',
    description='Small extension to make using rst easy',
    long_description=__doc__,
    py_modules=['flask_restructuredtext'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['Flask', 'docutils'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
