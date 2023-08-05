Flask-Whiteprint
================

Flask-Whiteprint is an enhancement of Flask-Blueprint.


Installation
------------

Flask-Whiteprint is on development. I recommend **NOT** using it now.


Whiteprint-level Error Handler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Flask-Whiteprint supports whiteprint-level error handler for all exceptions include 404 and 500. I'll remove that ending parentheses soon.

::

    @blueprint.errorhandler()
    def handle_error(e):
        data = {
            'error': {
                'code': e.code,
                'message': e.message
            }
        }
        return Response(data, mimetype='application/json', status=e.status)


Dynamic Alias URL
~~~~~~~~~~~~~~~~~

You can alias url with ``alias`` method. Alias redirects without any redirect response (e.g. 301 or 302) and with all request context (e.g. HTTP Header, URL Variables or Form Data). This code redirects ``/me`` to ``/user/<int:id>`` with all request context.

::

    @api.route('/me', methods=['GET', 'POST', 'PUT', 'DELETE'])
    @api.route('/me/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    @login_required
    @jsoned
    def redirect_me(path=''):
        if 'path' in request.view_args:
            request.view_args.pop('path')
        user_path = '/user/%d/' % current_user.id + path
        if user_path[-1] == '/':
            user_path = user_path[:-1]
        return api.alias(user_path, current_user.id)


Sub whiteprint (Not yet)
~~~~~~~~~~~~~~~~~~~~~~~~

You can add child whiteprints to another whiteprint.

::

    app (Flask Application)
    |-- api (Parent whiteprint)
    |   |-- auth (Child whiteprint)
    |   |   |-- login (Another child whiteprint)
    |   |   `-- logout
    |   |-- user
    |   `-- post
    |-- web (Another parent whiteprint)
    |   |-- auth
    |   |-- user
    |   `-- post
    `-- admin
        `-- admin

It looks awkward, but... just for an example!
