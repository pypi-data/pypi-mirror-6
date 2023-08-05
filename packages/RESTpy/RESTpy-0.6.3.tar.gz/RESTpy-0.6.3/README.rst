======
RESTpy
======

**Werkzeug utilities for building RESTful services.**

What is RESTpy?
===============

RESTpy is a small set of utilities built on Werkzeug that make it a little
easier to roll out a RESTful web service.

Simple Usage Example
====================

::

    from restpy.applications import RestApplication

    from werkzeug.routing import Map, Rule
    from werkzeug.wrappers import Response


    # URL endpoints are plain Python objects that expose methods matching
    # HTTP request verbs. Routing to the right method is handled by the
    # RestApplication object.
    class IndexEndpoint(object):

        def GET(self, request):
            return Response("GET")

        def POST(self, request):
            return Response("POST")

        def PUT(self, request):
            return Response("PUT")

        def DELETE(self, request):
            return Response("DELETE")

    # URL mappings are normal Werkzeug routing Maps.
    urls = Map([
        Rule("/", endpoint=IndexEndpoint)
    ])

    # This object can be exposed to any WSGI server.
    application = RestApplication(urls)

More Features
=============

Routing
-------

This package comes with a Werkzeug routing converter that recognizes UUIDs::

    from restpy.routing import UuidConverter

Request/Response Hooks
----------------------

The `RestApplication` constructor takes additional keyword arguments of
`request_hooks` and `response_hooks`. These allow for functions to modify the
request before it reaches the endpoint and the response before it is returned
to the web server.

Request hooks must be a callable that accept one argument which will be the
Werkzeug request object. Werkzeug uses read-only attributes in request objects
so existing attributes cannot be modified. New attributes, however, may be
added to the request. If the hook returns a Werkzeug request object then that
request will overwrite the original request object.

Response hooks must be a callable that accept two arguments which will be the
Werkzeug request and the Werkzeug response objects. These hooks may modify the
attributes of the Werkzeug response object. If the hook returns a Werkzeug
response object then that response will overwrite the original response object.

Included with this package is a pre-defined hook that may be used::

    # A request hook that adds a UUID to the request object.
    # UUID can be found at `request.uuid`.
    # If a UUID is already present in the WSGI environ then it is used.
    from restpy.hooks import unique_request

WSGI Middlewares
----------------

The `RestApplication` object is a plain WSGI application and is compatible with
any WSGI middleware.

Included with this package are some pre-defined middlewares that may be used::

    # Adds a UUID to the WSGI environ.
    from restpy.wsgi import UniqueEnvironMiddleware

    # Activates a Werkzeug response object and returns the final results
    # to the WSGI server.
    from restpy.wsgi import ResponderMiddleware

Pluggable Services
------------------

The `RestApplication` constructor allows for the first argument, normally a
Werkzeug `Map` object, to be an iterable of service objects. A service object
is a Python object with a `urls` attribute or a dictionary with a `urls` key.

The purpose of this feature is to allow for services to be developed
independently and then merged together into a simple WSGI application. For
example::

    ##################
    # service_one.py #
    ##################

    from werkzeug.routing import Rule
    from werkzeug.wrappers import Response

    class ServiceOneEndpoint(object):

        def GET(self, request):
            return Response("GET")

        def POST(self, request):
            return Response("POST")

        def PUT(self, request):
            return Response("PUT")

        def DELETE(self, request):
            return Response("DELETE")

    # URL mappings are simple iterables containing Werkzeug `Rule` objects.
    urls = [
        Rule("/service_one", endpoint=ServiceOneEndpoint)
    ]

    ##################
    # service_two.py #
    ##################

    from werkzeug.routing import Rule
    from werkzeug.wrappers import Response

    class ServiceTwoEndpoint(object):

        def GET(self, request):
            return Response("GET2")

        def POST(self, request):
            return Response("POST2")

        def PUT(self, request):
            return Response("PUT2")

        def DELETE(self, request):
            return Response("DELETE2")

    urls = [
        Rule("/service_two", endpoint=ServiceTwoEndpoint)
    ]

    ##########
    # app.py #
    ##########

    from restpy.applications import RestApplication

    import service_one
    import service_two

    application = RestApplication(services=[service_one, service_two])

From here the `RestApplication` object will build a Werkzeug `Map` that is a
composite of the two services URL mappings.

License
=======

This project is released under the same BSD license as Werkzeug::

    Copyright (c) 2013 by Kevin Conway

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are
    met:

        * Redistributions of source code must retain the above copyright
          notice, this list of conditions and the following disclaimer.

        * Redistributions in binary form must reproduce the above
          copyright notice, this list of conditions and the following
          disclaimer in the documentation and/or other materials provided
          with the distribution.

        * The names of the contributors may not be used to endorse or
          promote products derived from this software without specific
          prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
    A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
    OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
    SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
    LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
    DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
    THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Contributor's Agreement
=======================

All contributions to this project are protected by the contributors agreement
detailed in the CONTRIBUTING file. All contributors should read the file before
contributing, but as a summary::

    You give us the rights to distribute your code and we promise to maintain
    an open source release of anything you contribute.
