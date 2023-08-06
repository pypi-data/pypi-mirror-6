Nico Nico Douga (ニコニコ動画) Comment Translator
=================================================

Installation
------------

You can install it using ``pip``:

.. code-block:: console

   $ pip install niconico-translator


Aliasing ``msg.nicovideo.jp`` to localhost
------------------------------------------

To make the translator to intercept comments from Nico Nico comment server,
you have to alias Nico Nico comment server domain (``msg.nicovideo.jp``) to
your localhost (``127.0.0.1``).  Open your `hosts file`__ using text editor
(you probably need administrator permission), and then add the following line:

.. code-block:: text

   127.0.0.1    msg.nicovideo.jp

__ http://en.wikipedia.org/wiki/Hosts_%28file%29


Proxy server
------------

The translator behaves as a proxy server, so it has to be running while
you watch Nico Nico videos.  You can invoke the proxy server using CLI
(you probably need administrator permission to listen 80 port):

.. code-block:: console

   $ niconico-translator

You can terminate the server by pressing Ctrl-C.

It can optionally take the target language which is a two-letter
e.g. ``en``, ``ko``:

.. code-block:: console

   $ niconico-translator --language ko


Advanced use
------------

If you have a WSGI fetish, you can utilize it as a WSGI application.
It's actually an ordinary WSGI application, you can serve it using your
favorite WSGI server e.g. Gunicorn_:

.. code-block:: console

   $ gunicorn "niconico_translator:App('en')"

Every instance of ``niconico_translator.App`` implements ``__call__()`` method,
which is a WSGI application.

.. _Gunicorn: http://gunicorn.org/


Open source
-----------

It's written by `Hong Minhee`__, and distributed under AGPLv3_.  You can find
the source code from the repository__ (hg):

.. code-block:: console

   $ hg clone https://bitbucket.org/dahlia/niconico-translator

Please report bugs to the `issue tracker`__ if you find.  Pull requests welcome!

__ http://dahlia.kr/
.. _AGPLv3: http://www.gnu.org/licenses/agpl-3.0.html
__ https://bitbucket.org/dahlia/niconico-translator
__ https://bitbucket.org/dahlia/niconico-translator/issues
