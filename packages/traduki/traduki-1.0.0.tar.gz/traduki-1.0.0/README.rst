traduki: SQLAlchemy internationalisation
========================================

The ``traduki`` package provides internationalisation helper classes for SQLAlchemy-based projects.

.. image:: https://api.travis-ci.org/paylogic/traduki.png
   :target: https://travis-ci.org/paylogic/traduki
.. image:: https://pypip.in/v/traduki/badge.png
   :target: https://crate.io/packages/traduki/
.. image:: https://coveralls.io/repos/paylogic/traduki/badge.png?branch=master
   :target: https://coveralls.io/r/paylogic/traduki


Installation
------------

.. sourcecode::

    pip install traduki


Usage
-----

traduki usage example:

.. code-block:: python

    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    import traduki

    def get_current_language():
        """Current language callback for our project."""
        return request.locale

    def get_language_chain():
        """Language chain (fallback rule) callback for our project."""
        return {'*': request.locale}

    i18n_attributes = traduki.initialize(Base, ['en', 'ru'], get_current_language, get_language_chain)

    Session = sessionmaker(bind=engine)
    sess = Session()

    class MyModel(Base)

        title_id = i18n_attributes.i18n_column(nullable=False, unique=False)
        title = i18n_attributes.i18n_relation(title_id)
        """Title."""

    my_object = MyModel()
    my_object.title = {'en': 'English title', 'pt': 'Portugese title'}
    sess.add(my_object)
    sess.commit()

    assert sess.refresh(my_object).title.get_dict() == {'en': 'English title', 'pt': 'Portugese title'}


Contact
-------

If you have questions, bug reports, suggestions, etc. please create an issue on
the `GitHub project page <http://github.com/paylogic/traduki>`_.


License
-------

This software is licensed under the `MIT license <http://en.wikipedia.org/wiki/MIT_License>`_

See `License <https://github.com/paylogic/traduki/blob/master/LICENSE.txt>`_


© 2013 Paylogic International.
