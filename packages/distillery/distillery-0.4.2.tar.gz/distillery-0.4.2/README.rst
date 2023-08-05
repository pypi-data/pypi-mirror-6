Distillery
==========

.. image:: https://secure.travis-ci.org/Birdback/distillery.png

``distillery`` is another `factory_girl
<https://github.com/thoughtbot/factory_girl>`_ like library for python
ORMs.


Installation
------------

``pip install distillery``


Distilleries
------------

Each distillery has a ``__model__`` and a set of attributes and
methods. The ``__model__`` is the ORM model class from which instance
will be produced:

.. code-block:: python

    class UserDistillery(MyOrmDistillery):
        __model__ = User


Attributes
~~~~~~~~~~

A distillery class attribute defines default values for specific model
field:

.. code-block:: python

    class UserDistillery(MyOrmDistillery):
        __model__ = User

        username = "defaultusername"

The distillery's attribute values act as *defaults*. If a ``User``
object is created using this distillery, its ``username`` attribute
will default to ``"defaultusername"``.


Lazy attributes
~~~~~~~~~~~~~~~

Using the ``lazy`` decorator, you can provide dynamic attributes.

.. code-block:: python

    from distillery import lazy

    class UserDistillery(MyOrmDistillery):
        __model__ = User

        username = "defaultusername"

        @lazy
        def email_address(cls, instance, sequence):
            return "%s@%s" % (instance.username, instance.company.domain)

All new ``User`` created from ``UserDistillery`` will have an
``email_address`` computed from his username and his company domain.

Note: all lazies received an ``instance`` and a ``sequence`` that are
the object instance and an auto-incremented sequence, respectively.


Hooks
~~~~~

A distillery can provide an ``_after_create`` class method to hook
into the factory machinery.

.. code-block:: python

    class UserDistillery(MyOrmDistillery):
        __model__ = User

        username = "defaultusername"

        @classmethod
        def _after_create(cls, instance):
            # Do stuff after instance creation
            # ...


Distillery.init()
~~~~~~~~~~~~~~~~~

The ``init()`` method creates and populates a new instance.

.. code-block:: python

    user = UserDistillery.init()
    assert user.username == "defaultusername"
    assert user.id is None

    user = UserDistillery.create(username="overriddenusername")
    assert user.username == "overriddenusername"
    assert user.id is None


Distillery.create()
~~~~~~~~~~~~~~~~~~~

The ``create()`` method initializes the object using ``init()`` and
subsequently *saves* it.

.. code-block:: python

    user = UserDistillery.create()
    assert user.username == "defaultusername"
    assert user.id is not None


Distillery.bulk()
~~~~~~~~~~~~~~~~~

Creates instances in bulk.

.. code-block:: python

    users = UserDistillery.bulk(12, username="user_%(i)%")
    assert users[7].username = 'user_7'


Sets
----

The ``distillery.Set`` class acts as a fixture container.

It's required to define a ``__distillery__`` attribute which is used
to create objects.

.. code-block:: python

    from distillery import Set

    class UserSet(Set):
        __distillery__ = UserDistillery

        class jeanphix:
            username = 'jeanphix'


To create the fixtures, simply instantiate the set.

.. code-block:: python

    users = UserSet()
    assert users.jeanphix.username == 'jeanphix'

Importantly, as long as a reference to the *instantiated set* is held
(e.g. the ``users`` variable in this example), the set can be called
again and the same instance is returned:

.. code-block:: python

    assert UserSet() is UserSet()

You can reference other sets, too. Note that you must reference using
the class, or use a lazy attribute (described later):

.. code-block:: python

    from distillery import Set

    class CompanySet(Set):
        __distillery__ = CompanyDistillery

        class my_company:
            name = 'My company'

    class UserSet(Set):
        __distillery__ = UserDistillery

        class jeanphix:
            username = 'jeanphix'
            company = CompanySet.company


    users = UserSet()
    assert users.jeanphix.company == 'My company'


In addition to classes, methods can be defined; each will result in an
object which is added to the set.

.. code-block:: python

    class ProfileSet(Set)
        class __distillery__:
            __model__ = Profile

        admin = lambda s: UserDistillery.create(username='admin').profile

This functionality extends to class-based references. Note that the
reference must be resolvable at the point of creation; circular
relationships are currently not supported.

.. code-block:: python

    class UserSet(Set):
        class peter:
            friend = None

        class paul:
            friend = classmethod(lambda c: UserSet.peter)


If the ``on_demand`` flag is set, objects are created only when first
accessed.

.. code-block:: python

    users = UserSet(on_demand=True)
    users.jeanphix  # jeanphix will be created here.

Finally, sets can be nested.

.. code-block:: python

    class fixtures(Set):
        users = UserSet

    assert fixtures().users.jeanphix.username == 'jeanphix'


Hooks
~~~~~

Each fixture in a set can provide an ``_after_create`` listener:

.. code-block:: python

    class ProfileSet(Set):
        class __distillery__:
            __model__ = Profile

        class admin:
            @classmethod
            def _after_create(cls, profile):
                profile.name = 'Full name'

    assert ProfileSet().admin.name == 'Full name'


ORMs
----

Both Django and SQLAlchemy are supported.


Django
~~~~~~

Django models could be distilled using ``DjangoDistillery`` that only
requires a ``__model__`` class member:

.. code-block:: python

    from distillery import DjangoDistillery

    from django.auth.models import User

    class UserDistillery(DjangoDistillery):
        __model__ = User

        #  ...


SQLAlchemy
~~~~~~~~~~

SQLAlchemy distilleries require both the ``__model__`` and
``__session__`` attributes.

.. code-block:: python

    from distillery import SQLAlchemyDistillery

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite://', echo=False)
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    Base = declarative_base()

    class User(Base):
        #  ...


    class UserDistillery(SQLAlchemyDistillery):
        __model__ = User
        __session__ = session

        #  ...
