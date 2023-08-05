from flask import Blueprint, request
from exceptions import HTTPExceptionBase, NotAuthorizedError, PageNotFoundError
from werkzeug.exceptions import HTTPException
import traceback


class FakeHandler(dict):
    """A class for replacement of `app`'s `error_handler_spec[None]`."""

    def __init__(self, errorhandler):
        self.errorhandler = errorhandler

    def get(self, code, default=None):
        """Returns an predefined error handler instead of handler spec."""
        if code is None:
            return ()
        return self.errorhandler


class Whiteprint(Blueprint):

    #: a reference to the current application.
    app = None

    #: an registered error handler using decorator :meth:`errorhandler`.
    registered_errorhandler = None

    def register(self, app, options, first_registration=False):
        """Blueprint `register` method implementation. Overrides `app`'s
        default error handler spec(:meth:`error_handler_spec[None]`) to
        predefined class :class:`FakeHandler`.
        """
        super(Whiteprint, self).register(app, options, first_registration)
        if not isinstance(app.error_handler_spec[None], FakeHandler):
            app.error_handler_spec[None] = FakeHandler(self._handle_error)
        self.app = app

    def _handle_error(self, e):
        """Returns handled excpetion. Detects blueprint from global
        :class:`~flask.wrappers.Request` object, and passes exception object to
        its `registered_errorhandler`."""
        whiteprint = self.detect_whiteprint()

        if isinstance(e, HTTPException):
            if not hasattr(e, 'status'):
                if e.code == 401:
                    e = NotAuthorizedError()
                elif e.code == 404:
                    e = PageNotFoundError()
                else:
                    e.status = e.code
                    e.code = 0
                    e.message = e.description
        else:
            print traceback.format_exc()
            e = HTTPExceptionBase()

        if whiteprint and whiteprint.registered_errorhandler:
            return whiteprint.registered_errorhandler(e)
        return e

    def detect_whiteprint(self):
        """Returns detected whiteprint from request."""
        subdomain = request.host.split(self.app.config['SERVER_NAME'])[0][:-1]
        paths = request.path.split('/', 1)

        whiteprint = None
        max_len = 0
        for name, bp in self.app.blueprints.iteritems():
            if not isinstance(bp, Whiteprint):
                continue

            if (whiteprint, bp.subdomain, bp.url_prefix) == (None, None, None):
                whiteprint = bp
                continue

            if subdomain != bp.subdomain:
                continue

            if bp.url_prefix is None:
                whiteprint = bp
                break

            # detects whiteprint with `subdomain` and `url_prefix`.
            blueprint_paths = bp.url_prefix.split('/', 1)
            l = len([i for i, j in zip(paths, blueprint_paths) if i == j])
            if l > max_len:
                whiteprint = bp
                max_len = l

        return whiteprint

    def errorhandler(self):
        """Registers an error handler for this blueprint."""
        def decorator(f):
            self.registered_errorhandler = f
            return f
        return decorator

    def alias(self, path, *args, **kwargs):
        # Is this the best solution? ...No
        """client = app.test_client()
        url = 'http://' + request.host + user_path
        return client.open(url, method=request.method,
                           query_string=request.view_args, data=request.form)"""

        # A better solution.
        view_func = None
        for rule in self.app.url_map._rules:
            url_rule = 'api|' + path
            if rule.match(url_rule) and request.method in rule.methods:
                view_func = self.app.view_functions[rule.endpoint]
        if view_func is None:
            raise PageNotFoundError()

        request_uri = path + request.environ['REQUEST_URI'][3:]
        request.environ['REQUEST_URI'] = request_uri.encode('utf-8')
        request.environ['PATH_INFO'] = path.encode('utf-8')
        return view_func(*args, **kwargs)
