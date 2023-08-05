=====================
Flask-ReportableError
=====================

Introduction
------------

Flask-ReportableError is a Flask extension for handling errors that can
be reported to the web client.


Documentation
-------------

In order to use Flask-ReportableError, you must include the following
statement in you application start script::

    from flask import Flask
    import flask_reportable_error

    app = Flask(__name__)
    app.config.from_envvar('FLASK_SETTINGS', silent=True)
    flask_reportable_error.init(app)


API
---

- ``flask_reportable_error.init()``:
  context initializer, it must receive the application as parameter.


- ``flask_reportable_error.mixin``:
  class decorator that declares the decorated class as mixin with
  reportable exceptions.


- ``flask_reportable_error.reportable()``:
  factory to create reportable exception classes. For example::

    raise reportable(ValueError)('invalid data received')


- ``flask_reportable_error.ReportableErrorMixin``:
  mixin for reportable exception classes.

  - ``report()``:
    method that returns the reportable string – can be overridden.

  - ``status_code``:
    property representing the numeric status code – can be set at
    instance level.

  - ``template``:
    attribute refering to custom template name.

  - ``headers``:
    attribute refering to custom headers.

  - ``type_name``:
    attribute set by ``reportable()`` on inheritance, with the name of
    the original exception class.


Settings
--------

The Flask settings may contain the key ``REPORTABLE_ERROR``, that’s a
dictionary with the following keys:

- ``LOGLEVEL``:
  the logging level. If not supplied, Flask-ReportableError uses
  ``logging.ERROR``.

- ``DEFAULT_STATUS_CODE``:
  the default numeric status code for reportable exception classes. By
  default it’s 500.

- ``TEMPLATE``:
  the name of a template to be used instead of none. The context of the
  template will contain the exception as value of the ``exc`` key.

- ``HEADERS``:
  a dictionary to be used as default headers instead of ``{}``.
