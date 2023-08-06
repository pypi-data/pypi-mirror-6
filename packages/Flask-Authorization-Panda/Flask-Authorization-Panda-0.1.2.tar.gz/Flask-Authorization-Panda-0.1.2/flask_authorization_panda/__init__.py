"""
**Flask-Authorization-Panda is a Flask extension that provides decorators
for various authentication methods for RESTful web services.

Currently, only HTTP Basic Authentication is supported. **

Usage
-----

    >>> from flask.ext.flask_authorization_panda import basic_auth

During app initialization, store your required username/password in
the config attribute::

    app = Flask(__name__)
    app.config['basic_auth_credentials'] = dict(username='admin',
                                                password='secret')


Finally, simple apply the @basic_auth decorator to methods which you
want to require HTTP Basic Auth::

    >>> @app.route('/')
    >>> @basic_auth
    >>> def hello_world():
    >>>    return jsonify({"statusCode": 200, "message": "Ok"})

This will result in all calls against the decorated method to (1) check for
for credentials on the request.authorization object and (2) verify that
they match the contents of app.config['basic_auth_credentials]'

"""

__version__ = '0.1.2'

from basic_auth import basic_auth