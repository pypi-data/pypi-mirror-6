import sys
import traceback
import types
from jinja2 import Environment, PackageLoader

from .renderers import (
    BaseRenderer,
    Template,
    Json,
    Compress,
    Format,
    BulkRenderer
)


class MethodRenderer(list):
    '''
    The ``MethodRenderer`` provides an interface for multiple renderers to all
    manipulate the controller method's output in an orderly fashion.

    It should be noted that the ``MethodRenderer`` class inherits from
    :func:`list`. The first item in the list should always be an instance
    of :class:`gimme.controller.ControllerMethod`. Every other item should
    inherit from :class:`gimme.renderers.BaseRenderer`.
    '''
    def __init__(self, items=[]):
        if len(items) < 1 or not isinstance(items[0], ControllerMethod):
            raise ValueError("First argument to MethodRenderer must be "
                "an instance of ControllerMethod")

        self.im_class = items[0].im_class
        self.__name__ = items[0].__name__
        list.__init__(self, items)

    def __call__(self):
        '''
        Calls the :class:`ControllerMethod <gimme.controller.ControllerMethod>`
        and then calls :meth:`render` on each of the
        :class:`BaseRenderer <gimme.renderers.BaseRenderer>` objects.

        :return: The final output of the execution chain described above.
        '''
        controller = self[0].controller_instance
        data = self[0]()

        for i in self[1:]:
            data = i.render(controller, data)

        return data

    def __add__(self, other):
        '''
        Adds another :class:`BaseRenderer <gimme.renderers.BaseRenderer>` to
        the list.

        :param BaseRenderer other: The renderer to add.
        :return: self
        '''
        if not isinstance(other, BaseRenderer):
            other = Template(other)
        self.append(other)
        return self

    def __repr__(self):
        return "<MethodRenderer([%s])>" % ', '.join(map(str, self))

    def __eq__(self, content_type):
        '''
        Returns a :class:`Format <gimme.renderers.Format>` object with all of
        the renderers in this object inside it. Sets the ``Format`` content
        type to ``content_type``.

        This is typically used in something like the following::

            app.routes.get('/', SomeController.index + (
                (SomeController.index == 'text/plain') |  # <--
                (SomeController.index.json() == 'application/json') |
                (SomeController.index.template('template.html') == 'text/html')
            ))

        :param str content_type: The content type to set the ``Format`` object
            to.
        :return: A :class:`Format <gimme.renderers.Format>` object.
        '''
        return Format(BulkRenderer(list(self[1:])), content_type)

    def template(self, template_path):
        '''
        Adds a :class:`Template <gimme.renderers.Template>` object with the
        provided path to the list.

        :param str template_path: The path to the template
        :return: self
        '''
        self.append(Template(template_path))
        return self

    def json(self):
        '''
        Adds a :class:`Json <gimme.renderers.Json>` object to the list.

        :return: self
        '''
        self.append(Json())
        return self

    def compress(self):
        '''
        Adds a :class:`Compress <gimme.renderers.Compress>` object to the list.

        :return: self
        '''
        self.append(Compress())
        return self


class ControllerMethod(object):
    '''
    ControllerMethod objects wrap regular controller methods, as defined by
    the application programmer.

    In order to allow greater flexibility and expressiveness, all controller
    methods whose name do not start with ``_`` are replaced with instances of
    ``ControllerMethod``. These objects can be called just as the controller
    methods can, but in addition, other methods and operators are made
    available.

    What all this means, in practice, is that you can do things like this in
    your route definitions::

        app.routes.get('/', RootController.index + 'index.html')

    I hope to elaborate on this and how it works in the future.
    '''

    def __init__(self, cls, fn):
        self.im_class = cls
        self.fn = fn
        self.__name__ = fn.__name__

    def __call__(self):
        return self.fn(self.controller_instance)

    def __add__(self, other):
        '''
        Creates a new :class:`gimme.controller.MethodRenderer` object with
        the ``other`` object as the first renderer. Or, if ``other`` is a
        string, instantiates a :class:`gimme.renderers.Template` object with
        the string and passes that to the
        :class:`gimme.controller.MethodRenderer` instead.

        Example::

            method_renderer = SomeController.some_method + gimme.Template('index.html')
            # or, a shortcut:
            method_renderer = SomeController.some_method + 'index.html'

        :param other: Either a string or an instance of
            :class:`gimme.renderers.BaseRenderer`.
        '''
        if not isinstance(other, BaseRenderer):
            other = Template(other)
        return MethodRenderer([self, other])

    def __eq__(self, content_type):
        '''
        Returns a :class:`gimme.renderers.Format` object that responds to
        HTTP Accept headers as specified by ``content_type``.

        Example::

            format_obj = YourController.your_method == 'text/html'

        :param str content_type: The content type to customize format to.
        '''
        return Format(BulkRenderer([]), content_type)

    def template(self, template_path):
        '''
        Returns a :class:`gimme.controller.MethodRenderer` object with a
        :class:`gimme.renderers.Template` renderer directed at the path
        provided by ``template_path``.

        :param str template_path: Where to point the template to.
        '''
        return MethodRenderer([self, Template(template_path)])

    def json(self):
        '''
        Returns a :class:`gimme.controller.MethodRenderer` object with a
        :class:`gimme.renderers.Json` renderer.
        '''
        return MethodRenderer([self, Json()])

    def compress(self):
        '''
        Returns a :class:`gimme.controller.MethodRenderer` object with a
        :class:`gimme.renderers.Compress` renderer.
        '''
        return MethodRenderer([self, Compress()])


class ControllerMeta(type):
    def __init__(mcs, name, bases, attrs):
        for key, value in [(k, v) for (k, v) in attrs.iteritems()
                if not k.startswith('_')]:
            if hasattr(value, '__call__'):
                setattr(mcs, key, ControllerMethod(mcs, value))

        type.__init__(mcs, name, bases, attrs)


class Controller(object):
    '''
    Like most frameworks, the controller is what bridges the gap between the
    model (business logic) and the view. In Gimme, one thing that is a little
    different from the classic MVC methodology is that controllers are not
    directly tied to views. This is explained further in the
    :class:`gimme.routes.Routes` documentation.

    Controllers are instantiated automatically by Gimme on an as-needed basis.
    If a controller's method is needed to fulfill a request, the controller
    will be instantiated and the method called and its data returned. This
    means that controllers are instantiated per request, as opposed to once,
    as the application is started.

    One thing to note is that, while Gimme instantiates controllers
    automatically, in order to perform unit tests, you must instantiate
    controllers in your tests. This can be done like so::

        controller = YourController(your_app, request_obj, response_obj)

    Of course, to do the above, you must have request and response objects.
    To fetch these objects, the easiest way is generally via the
    :meth:`gimme.routes.Routes.match` method::

        request, response = your_app.routes.match(wsgi_environ)

    (Where the ``wsgi_environ`` variable is a dictionary-like object with
    necessary WSGI environ parameters, such as ``PATH_INFO``,
    ``REQUEST_METHOD``, etc.)

    One other thing that may be worth noting is that this class uses a
    custom metaclass that, upon definition, scans for any method whose name
    does not start with a ``_``, and replaces it with an instance of
    :class:`gimme.controller.ControllerMethod`.

    :ivar app: The gimme app.
    :ivar request: The request object.
    :ivar response: The response object.
    '''
    __metaclass__ = ControllerMeta

    def __init__(self, app, request, response):
        self.app = app
        self.request = request
        self.response = response

    def __new__(cls, *args):
        obj = object.__new__(cls, *args)

        for i in dir(obj):
            attr = getattr(obj, i)
            if isinstance(attr, ControllerMethod):
                attr.controller_instance = obj

        return obj


class ErrorController(Controller):
    def __init__(self, *args, **kwargs):
        Controller.__init__(self, *args, **kwargs)
        self.environment = Environment(
            loader=PackageLoader('gimme', 'templates'))

    def http404(self):
        self.response.status = 404

        return self.environment.get_template('errors/404.html').render({
            'headers': self.request.headers,
        })

    def http500(self):
        self.response.status = 500
        e_type, e_value, e_traceback = sys.exc_info()
        traceback.print_exception(e_type, e_value, e_traceback)

        return self.environment.get_template('errors/500.html').render({
            'message': "Oh snap! Something's borked. :(",
            'headers': self.request.headers,
            'traceback': traceback.format_exception(
                e_type,
                e_value,
                e_traceback)
        })

    def generic(self):
        return self.environment.get_template('errors/generic.html').render({
            'status': self.response._status
        })
