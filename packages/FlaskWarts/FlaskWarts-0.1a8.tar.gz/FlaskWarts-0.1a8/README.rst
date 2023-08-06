===========
FlaskWarts
===========

FlaskWarts are a set of utility classes and functions for making it easier to
overcome some of the warts that one always seem to encounter when developing
Flask applications. It's called 'warts' because 'utils' was taken. The main
package is still called ``utils``, because that's what it was called in a few
apps author was using the code in, and was too lazy to refactor them all.

Overview
========

The library is not too generic. In fact, it's quite opinionated. It's made
available as is if you care to use it, but it's mainly there for the author's
use cases.

While not an immediate goal, it is author's intention to make this a
fully-comliant Flask extension at some point, and far more flexible. It may be
brokend down into multiple separate libraries as well. Currently, it is a
multi-purpose library that expects you to organize your site as a single
application and uses ``flask.current_app`` extensively. While this is not a
good pattern in general, it's a pattern that works (for the time being).

It also expects that you place your configuration in ``app.config``.

Note that not all code is fully developed and tested. Some of the code even
misses unit tests, and documentation doesn't exist. So this is pretty much
pre-alpha software. Also, don't expect anything in the way of API stability in
any form.

Features
========

The utils have following features:

+ Class-based route handlers (``utils.routes``)
+ Form-handling with Formencode (``utils.forms``)
+ CSRF middleware (``utils.middlewares``)
+ Basic timezone manipulation support (``utils.timezone``)
+ One decorator for denying non-XHR requests (``utils.decorators``)

Installation
============

Either::

    easy_install FlaskWarts

Or::

    pip install FlaskWarts


Class-based route handling
==========================

Please see the sources for now. More detailed docs are planned for future
releases. It's similar to Django's CBVs but not quite the same.

Simple example::

    from flask import render_template
    from utils.routes import Route

    class MyRoute(Route):
        path = '/my'

        def GET(self):
            return render_template('foo.html')

Method names correspond to HTTP methods, and any positional or keyword
arguments in the paths are passed as positional and keyword arguments to the
method. In addition, the positional and keyword arguments are accessible as
``self.args`` and ``self.kwargs``, a list and dict respectively.

Methods are expected to return a response just like normal flask route handler
functions.

By default, HTTP method overrides are supported via the ``_method`` request 
parameter for all POST requests, and the ``Route`` class intelligently maps
them to the correct instance method. This is handled transparently behind the
scenes so you don't have to worry about it. You can disable this behavior, by
setting the ``allow_overrides`` property to ``False`` in your subclass.

There are many subclasses of the ``Route`` class which implement different
interfaces for common tasks like form processing and template rendering. Some
of them implement multiple HTTP methods. For now you will have to look at the
sources to find out more.

Routes are reigstered by calling the ``register()`` class method, and passing
it an application object::

    MyRoute.register(app)

The route name can be explicitly specified using the ``name`` property.
Otherwise, it is derived from the class name by decamelizing it. For instance,
``MyRoute`` has a name of ``my_route``. ``Foo`` has a name of ``foo``, and so
on.

If you organize routes into modules (e.g., have multiple route classes in a
single module), you can register them in batches. ::

    from utils.routes import register_module
    register_module(app, 'myapp.routes')

The ``register_module()`` function will register any object that has
``register()`` and ``get_route_name()`` attributes, and whose path attribute is
not ``None``. This is generally a good enough set of rules to catch all routes,
but if you have objects that accidentally fulfill the conditions, the function
will try to register it, so be careful.

If you want to explicitly exlude routes, you can use the ``exclude`` argument.
This argument should be an iterable containing names of classes or route names.

For instance::
    
    register_module(app, 'myapp.routes', exclude=['Test', 'mickey_mouse'])

The above excludes classes ``Test`` and ``MickeyMouse``.

Form-handling with Formencode
=============================

Allows basic form validation using Formencode's ``htmlfill_schemabuilder``.
Docs on the way, so stay tuned.

CSRF middleware
===============

A bit rough at the moment, but works. Uses ``os.urandom`` for random number
generation, you've been warned. It also makes Jinja2 a requirement.

Basic usage is simply::

    from utils.middlewares import csrf
    csrf(app)

In template::

    <form method="POST">
        {{ csrf_tag }}
        ...
    </form>

Docs? Who said anything about docs? :D

Timezone manipulation
=====================

Requires pytz_. Again, no docs yet, so please look at the module.

Decorators
==========

To prevent non-XHR requests to your endpoint, just do this::

    from utils.decorators import xhr_only

    @app.route('/')
    @xhr_only
    def my_view():
        pass

It will abort a non-XHR request with HTTP 400 status.


.. _pytz: http://pytz.sourceforge.net/

