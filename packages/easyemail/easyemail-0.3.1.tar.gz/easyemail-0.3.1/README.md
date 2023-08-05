easyemail
=========

Small lib abstracting creation and sending emails with smtplib. This is work in
progress, please do not use it in production.

WARNING
-------

From version 0.3 and up I stopped supporting template rendering inside of the
library. Now you need to render html / text on your side and use attach_text.

Installation
------------

Install with pip::

    $ pip install easyemail

Testing
-------

To run tests, you'll need `mako` and `jinja2` libraries that are not included
in requirements in normal setup.

You can run tests that way::

    $ python setup.py test

Issues and questions
--------------------

Have a bug? Please create an issue on GitHub!

https://github.com/niktto/easyemail/issues


Contributing
------------

EasyEmail is an open source software and your contribution is very much
appreciated.

1. Check for
   open issues https://github.com/niktto/easyemail/issues or
   open a fresh issue https://github.com/niktto/easyemail/issues/new
   to start a discussion around a feature idea or a bug.
2. Fork the
   repository on Github https://github.com/niktto/easyemail
   and make your changes.
3. Follow these rules: PEP8, PEP257 and The
   Zen of Python.
4. Make sure to add yourself to AUTHORS and send a pull request.


Licence
-------

EasyEmail is available under the New BSD License. See
LICENSE https://github.com/niktto/easyemail/blob/master/LICENSE
file.
