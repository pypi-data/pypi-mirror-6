gserver 0.2.0
==============

Simple wrapper around `gevent`_ that provides a basic routing engine
and JSON/JSONP handling.

Here's a simple usage example::

    from gevent.monkey import patch_all; patch_all()
    from gevent import queue

    from gserver.routes import Routes
    from gserver.request import parse_vals
    from gserver.wsgi import WSGIServer

    routes = Routes()
    route = routes.route
    route_json = routes.route_json

    @route("^/example/$")
    def example(req):
        return "hello"

    @route("^/poll/$")
    def poll(request):
        yield ' ' * 1000
        yield "hello"
        sleep(5)
        yield "goodbye" # connection is closed at this point

    @route("^/queue/$")
    def q(request):
        def process(b):
            b.put("<div>1</div>")
            sleep(1)
            b.put("<div>2</div>")
            sleep(1)
            b.put("<div>3</div>")
        
        body = queue.Queue()
        body.put(' ' * 1000)
        body.put("<!doctype html><html><head><title>hola</title><head><body>\n")
        gevent.spawn(process, body)
        return body

    @route_json("^/example/(?P<name>\w+)/$", method="GET,POST")
    def example_name(request, name=None):
        data = request.query_data
        if request.method == "POST":
            data = request.form_data
        query_age, query_height = parse_vals(data, "age", "height")

        return { "name": name,
                 "age": query_age,
                 "height": query_height }

    if __name__ == "__main__":
        server = WSGIServer(('', 9191), routes, log=None)
        server.serve_forever()

get gserver
===========

Install `gevent`_, and it's dependencies `greenlet`_ and `libevent`_::

    sudo easy_install gserver

Download the latest release from `Python Package Index`_ 
or clone `the repository`_

More documentation is on it's way *(check the* `site`_ *for updates)*

Provide any feedback and issues on the `bug tracker`_, that should be coming soon.


.. _gevent: http://www.gevent.org
.. _greenlet: http://codespeak.net/py/0.9.2/greenlet.html
.. _libevent: http://monkey.org/~provos/libevent/
.. _site: https://bitbucket.org/juztin/gserver
.. _the repository: https://bitbucket.org/juztin/gserver
.. _bug tracker: https://bitbucket.org/juztin/gserver
.. _Python Package Index: http://pypi.python.org/pypi/gserver
