# -*- coding: utf-8 -*-
"""Easy integration of RestructuredText.

flaskext.restructuredtext
~~~~~~~~~~~~~~~~~~~~~~~~~

reStructuredText filter class for Flask.

:copyright: (c) 2014 by Dennis Fink.
:license: BSD, see LICENSE for more details.

"""

from collections.abc import Sequence, Set

from flask import Markup
from jinja2 import evalcontextfilter, escape

from docutils.core import publish_parts
from docutils.parsers.rst import directives, roles
from docutils.writers.html4css1 import Writer as HTMLWriter


def _multiple_names(object):
    return isinstance(object, (Sequence, Set)) and not isinstance(object, str)


class ReStructuredText(object):

    """Easy integration of reStructuredText.

    This class is used to control the ReStructuredText integration to one
    or more Flask applications. Depending on how you initialize the
    object it  is usable right away or will attach as needed to a
    Flask application.

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

    def __init__(self, app=None, writer=HTMLWriter(), auto_escape=False):
        self.app = app
        self.writer = writer
        if app is not None:
            self.init_app(app, writer, auto_escape)

    def init_app(self, app, writer=None, auto_escape=False):
        """
        Configure an application.

        This registers an jinja2 filter, and attaches this `ReStructuredText`
        to `app.extensions['rst']`.

        :param app: The :class:`flask.Flask` object configure.
        :type app: :class:`flask.Flask`
        :param writer: The :class:`docutils.writers.Writer` object to use.
            Defaults to :class:`docutils.writers.html4css1.Writer`.
        :type writer: :class:`docutils.writers.Writer`
        :param auto_escape:Whether to auto_escape. Defaults to ``False``.
        :type auto_escape: bool

        """

        if not hasattr(app, 'extensions'):
            app.extensions = {}

        if writer is not None:
            self.writer = writer

        app.extensions['rst'] = self
        app.add_template_filter(self.__build_filter(auto_escape), name='rst')

    def __call__(self, stream):
        return publish_parts(stream, writer=self.writer)['html_body']

    def __build_filter(self, app_auto_escape):
        @evalcontextfilter
        def rst_filter(eval_ctx, stream):
            if app_auto_escape and eval_ctx.autoescape:
                return Markup(self(escape(stream)))
            else:
                return Markup(self(stream))
        return rst_filter

    @staticmethod
    def add_directive(directive_class, name=None):
        """
        Register a directive.

        Works exactly like the :meth:`directive` decorator.

        :param directive_class: The object to use.
        :param name: The name(s) to register the directive under.
            Defaults to the class name.
        :type name: str, list, tuple, set, frozenset

        """
        if _multiple_names(name):
            for directive_name in name:
                directives.register_directive(directive_name,
                                              directive_class)
        else:
            directives.register_directive(name or directive_class.__name__,
                                          directive_class)

    def directive(self, name=None):
        """
        Decorator to register directives.

        You can specify a name for the directive, otherwise the class
        name will be used. Example::

            @rst.directive()
            class Image(Directive):

                required_arguments = 1
                optional_arguments = 0
                final_argument_whitespace = True
                option_spec = {'alt': directive unchanged,
                    'height': directives.nonnegative_int,
                    'width': directives.nonnegative_int,
                    'scale': directivs.nonnegative_int,
                    'align': align,
                    }
                has_content = False

                def run(self):
                    reference = directives.uri(self.arguments[0])
                    self.options['uri'] = reference
                    image_node = nodes.image(rawsource=self.block_text,
                        **self.options)
                    return [image_node]

        You can also register a directive under more names, by setting the
        name parameter to an iterable with names in it. Example::

            @rst.directive(names=['image', 'img'])
            class Image(Directive):
                ...

        :param name:The name(s) to register a directive under.
            Defaults to the class name.
        :type name: str, list, tuple, set, frozenset

        """
        def decorator(f):
            self.add_directive(f, name=name)
            return f
        return decorator

    @staticmethod
    def add_role(role_function, name=None):
        """
        Register a role.

        Works exactly like the :meth:`role` decorator.

        :param role_function: The function to use.
        :param name: The name(s) to register the role under.
            Defaults to the function name.
        :type name: str, list, tuple, set, frozenset

        """
        if _multiple_names(name):
            for role_name in name:
                roles.register_local_role(role_name, role_function)
        else:
            roles.register_local_role(name or role_function.__name,
                                      role_function)

    def role(self, name=None):
        """
        Decorator for registering roles.

        You can specify a name for the role, otherwise the function
        name will be used. Example::

            @rst.role()
            def rfc(role, rawtext, text, lineno, inliner,
                    options={}, content=[]):
                try:
                    rfcnum = int(text)
                    if rfcnum <= 0:
                        raise ValueError
                except ValueError:
                    msg = inliner.reporter.error(
                     'RFC number must be number greater than or equal to 1;'
                     '"%s" is invalid.' % text, line=lineno)
                    return [prb], [msg]
                # Base URL mainly used by inliner.rfc_reference, so this is
                # correct:
                ref = (inliner.document.settings.rfc_base_url + inliner.rfc_url
                        % rfcnum
                set_classes(options)
                node = nodes.reference(rawtext, 'RFC' + utils.unescape(text),
                                       refuri=uri, **options)
                return [node], []

        You can also register a role under more names, by setting the name
        parameter to an iterable with names in it. Example::

            @rst.role(name=['rfc', 'rfc-reference'])
            def rfc(role, rawtext, text, lineno, inliner,
                    options={}, content={}):
                ...

        :param name:The name(s) to register to role under.
            Defaults to the function name.
        :type name: str, list, tuple, set, frozenset

        """

        def decorator(f):
            self.add_role(f, name=name)
            return f
        return decorator


def add_mapping_roles(mapping):
    """Register roles specified in a mapping.

    Keys should be the name to register the role under and
    the value should be the function to use.

    :param mapping:The mapping to use.
    :type name:Mapping

    """
    for name, role in mapping.items():
        ReStructuredText.add_role(role, name)


def add_mapping_directives(mapping):
    """Register directives specified in a mapping.

    Keys should be the name to register the directive under and
    the value should be the class to use.

    :param mapping:The mapping to use.
    :type name:Mapping

    """
    for name, directive in mapping.items():
        ReStructuredText.add_directive(directive, name)
