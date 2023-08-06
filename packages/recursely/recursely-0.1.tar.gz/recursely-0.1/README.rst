recursely
=========

Recursive importer for Python submodules and subpackages

.. image:: https://secure.travis-ci.org/Xion/recursely.png
   :alt: Build Status
   :target: http://travis-ci.org/Xion/recursely


Why?
~~~~

Nowadays, there are quite a few popular frameworks that use
modern Python features - like decorators - to organize code.
This keeps it concise and  `DRY <http://en.wikipedia.org/wiki/Don%27t_Repeat_Yourself>`_.
but presents a challenge when it comes to tying everything together.

As an example, if you use a web framework such as `Flask <http://flask.pocoo.org>`_,
you typically don't have a central place in code that maps URL patterns
to request handlers. Instead, you define your handlers like this::

    @app.route('/')
    def hello():
        return "Hello world!"

and it makes them available automatically.

However, once you start putting them into different modules,
you need to ensure they are all actually *imported*.
The way it's typically done borders on
`circular imports <http://flask.pocoo.org/docs/patterns/packages/>`_
and requires either repetition or some *ad-hoc* hacks.

Note that same issues may arise when using an ORM library,
developing a plugin system, and so on.


What?
~~~~~

*recursely* sets to deal with those issues in a more standarized, systemic way.

The idea is to avoid putting any explicit or implicit ``import submodule``
statements in package's `__init__.py`. file They introduce dependencies that
just shouldn't be there, and only narrowly avoid circular imports by their
sole placement at the bottom, rather than the top of the file.

Instead of those fragile ``import``\ s, with *recursely* you can just say::

    __recursive__ = True

and put this line anywhere in the file, even at the very top.
In fact, I recommend placing it right after module's docstring.

There's of course some setup involved, but it's quite trivial. You only
need to install *recursely*::

    import recursely
    recursely.install()

at some early stage of your program's initialization, before all the imports.
Putting this on top of your main package's `\_\_init\_\_.py` should be enough
in vast majority of cases.


How?
~~~~

So, what's the trick?... *recursely* uses a simple **import hook** to inspect
every imported module and check for the presence of ``__recursive__`` directive.
If it's found, its submodules and subpackages are imported automatically,
and this proceeds further to their submodules and subpackages, and so on.

But aren't import hooks Deep Magic™?
------------------------------------

Actually, the only real problem with import hooks is their composability:
making several hooks works together and not stomp on each other.
That's why *recursely* goes to great lengths to ensure that
its catch-all hook is always invoked as the *last* one.
This allows other, specialized hooks - like the one handling
`flask.ext pseudopackage <http://flask.pocoo.org/docs/extensiondev/>`_
- to operate without any issue on imports they are designed to intercept.


Where?
~~~~~~

*recursely* is available from PyPI::

    $ pip install recursely

License is BSD. Contributions are welcome!
