============
Wando Server
============

Wando Server is a beautiful web server for development - it is not intended to be a production server. 
This server is a extension to the really good dev server of `Werkzeug Project <http://werkzeug.pocoo.org>`_. Basically it prints more readable logs to the terminal.

It exposes the same api of "run_simple" method from `werkzeug.serving <http://werkzeug.pocoo.org/docs/serving>`_. You can run the server with this simple code::

    #!/usr/bin/env python
    from wando import run_simple
    from my_app import app

    run_simple(app, 'localhost', 5000)

If you using Flask, for example, you can just do::

    #!/usr/bin/env python                                                            
    from wando import ColoredLogsRequestHandler                                      
    from my_app import app                                                           
                                                                                 
    app.run(request_handler=ColoredLogsRequestHandler)
