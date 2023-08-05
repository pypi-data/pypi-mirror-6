#coding: utf-8

__version__ = '0.5.0'
__author__ = u'Marek Waluś <marekwalus@gmail.com>'


__all__ = ['Service', 'Route']

from resttouch.params import param_types
from parsers import plain
from requests import Request, Session
from urlparse import urljoin

AVAILABLE_METHODS = [
    'GET',
    'OPTIONS',
    'POST',
    'PUT',
    'PATCH',
    'DELETE'
]


class Route(object):
    #: Reference to service instance
    service = None
    #: Route name in service class
    name = ''

    def __init__(self, method, url, params, request_kwargs=None, session_kwargs=None):
        """
        Initialize route

        :param method: Method name: `GET`, `OPTIONS`, `POST`, `PUT`, `PATCH` or `DELETE`
        :param url: Route url, may be python string template if path parameters are defined in `params`
        :param params: List of route parameters, :class Param: instances
        :param request_kwargs:  Arguments as dict for request instance, override service `request_globals`
        :param session_kwargs: Arguments as dict for session instance. override service `session_globals`
        """
        assert method in AVAILABLE_METHODS, \
            'Unrecognized method: %s' % method

        self.method = method
        self.url = url
        self.params = dict((param.value, param) for param in params)
        self.request_kwargs = request_kwargs if request_kwargs else {}
        self.session_kwargs = session_kwargs if session_kwargs else {}

    def __call__(self, **kwargs):
        """
        Prepare data and start request

        :kwargs: keyword arguments
        """
        # Check if all keyword arguments are defined in route
        for name, value in kwargs.iteritems():
            if name not in self.params:
                raise ValueError("Unknown parameter: %s, available parameters: " % name +
                                 ", ".join([p for p in self.params]))

        for name, param in self.params.iteritems():
            # Add default parameters to keyword arguments
            if name not in kwargs and param.default:
                kwargs[name] = param.default

            # If parameter is marked as required and not in keyword arguments
            elif name not in kwargs and param.required:
                raise ValueError('%s param is required!' % name)

        # group keyword argument by parameter base class
        groups = dict((p, {}) for p in param_types)
        for name, value in kwargs.iteritems():
            for cls_name, cls in param_types.iteritems():
                if isinstance(self.params[name], cls):
                    groups[cls_name].update({name: value})

        # Create Session and Request instance
        session = Session()
        request = Request(
            method=self.method,
            url=urljoin(self.service.end_point, self.url % groups['PathParam']),
            params=groups['QueryParam'],
            data=self.service.input_data_parser.im_func(groups['DataParam']),
            files=groups['FileParam'],
            **dict(self.service.request_globals, **self.request_kwargs)
        )
        # prepare_request
        prepped = session.prepare_request(request)

        # Trigger before_request
        if hasattr(self.service, 'before_request'):
            prepped = self.service.before_request(prepped)

        # Send request
        response = session.send(prepped, **dict(self.service.session_globals, **self.session_kwargs))

        # Trigger after_request
        if hasattr(self.service, 'after_request'):
            response = self.service.after_request(response)

        # Trigger status code
        if hasattr(self.service, '%s_on_%s' % (self.name, response.status_code)):
            response = getattr(self.service, '%s_on_%s' % (self.name, response.status_code))(response)

        return self.service.output_parser.im_func(response)


class RouteMetaClass(type):
    def __new__(cls, name, bases, attrs):
        attrs['routes'] = [
            (route_name, obj) for route_name, obj in attrs.iteritems() if isinstance(obj, Route)
        ]
        return super(RouteMetaClass, cls).__new__(cls, name, bases, attrs)


class Service(object):
    __metaclass__ = RouteMetaClass

    end_point = 'localhost'
    routes = []
    request_globals = {}
    session_globals = {}
    input_data_parser = plain
    output_parser = plain

    def __init__(self):
        """
        Initialize service
        """
        # Add service reference to all routes
        for name, route in self.routes:
            route.service = self
            route.name = name