tt_dataviews
============
Django class-based views (CBVs) for `Texas Tribune's`__ data applications.

.. __: http://www.texastribune.org/

Note, this is not a complete solution for building data applications like the
Texas Tribune.  Instead, it's opened as an insight into how we structure part
of our applications.  It's meant to be a learning tool, not used directly.

That said, if you're interested, feel free to dive in.


Conventions
-----------

Static Assets
"""""""""""""
*TODO*

Landing Pages
"""""""""""""
*TODO*

Detail Pages
""""""""""""
*TODO*


Developing
----------
You need `Grunt`_ installed to develop the static assets associated with this
(see Grunt's `Getting Started`_ guide for more information on setting up Grunt).
Once you have Grunt installed, you need to install the development packages via
npm like this::

	npm install .

Once everything is installed, you can build the Sass with this command::

	grunt sass

There is also a convenience method for continually building the Sass files via
the ``watch`` command like this::

	grunt watch


.. _Grunt: http://gruntjs.com/
.. _Getting Started: http://gruntjs.com/getting-started
