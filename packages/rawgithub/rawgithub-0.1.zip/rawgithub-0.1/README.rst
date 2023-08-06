RawGithub
=========

rawgithub is a simple wsgi server that allows you to serve a file from Github even if you need to provide an access_token.

Just do:

    GET /:owner/:repo/:file?[access_token=<your_token>]&[ref=master]

And that's all.


Run the service
+++++++++++++++

    pserve rawgithub.ini


Run with WSGI
+++++++++++++

.. code:: python

    # -*- coding: utf-8 -*-
    import os

    cfg_dir = os.path.dirname(__file__)
    env_dir = os.path.join(cfg_dir, 'var', 'venv')

    activate_this = os.path.join(env_dir, 'bin', 'activate_this.py')
    execfile(activate_this, dict(__file__=activate_this))

    from pyramid.paster import get_app, setup_logging
    ini_path = os.path.join(cfg_dir, 'rawgithub.ini')
    setup_logging(ini_path)
    application = get_app(ini_path, 'main')
