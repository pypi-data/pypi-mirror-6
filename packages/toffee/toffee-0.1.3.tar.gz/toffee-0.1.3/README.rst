Toffee – test object factories
==============================


Toffee helps create test fixtures for ORM model objects.

Example::

    from toffee import Fixture, Factory

    product_factory = Factory(Product, id=Seq())

    class MyFixture(Fixture):

        product_1 = product_factory(desc='cuddly toy')
        product_2 = product_factory(desc='toy tractor')

        user = Factory(User, username='fred')
        order = Factory(Order, user=user, products=[product_1, product_2])


    def test_product_search():

        fixture = MyFixture()
        fixture.setup()

        assert fixture.product_1 in search_products('toy')
        assert fixture.product_2 in search_products('toy')
        ...

        fixture.teardown()

Toffee is similar in scope to 
`factory_boy <https://github.com/dnerdy/factory_boy>`_.
The differences that prompted me to write a new library are:

- Toffee promotes working with on fixtures as groups of objects to be created
  and destroyed as a unit, rather than individual factories
- Explicit support for setup/teardown of fixtures

Use with Django
---------------

To use this with Django's ORM, import DjangoFactory, which knows how to create
and delete Django model objects correctly::

    from toffee import DjangoFactory as Factory
    from myapp.models import Product

    class MyFixture(Fixture):
        product_2 = Factory(Product, desc='toy tractor')


Use with Storm
--------------

To use this with the `Storm ORM <http://storm.canonical.com/>`_,
import StormFactory, which knows how to create
and delete objects with Storm::

    from toffee import StormFactory
    from myapp.models import Product

    from storm.database import create_database
    from storm.store import Store

    database = create_database('sqlite:')
    Factory = StormFactory.configure(lamdba: Store(database))

    class MyFixture(Fixture):
        product_2 = Factory(Product, desc='toy tractor')

Flushing and commiting
``````````````````````

By default the StormFactory will call ``store.flush()`` at the end of setup,
but will not commit. 
This ensures that database generated values are populated,
(eg autoincrement ids)
but the fixture data will not be persisted 
until you explicitly call ``store.commit()``.

To change this behavior, override ``factoryoptions`` in your fixture class::

  class MyFixture(Fixture):

    factoryoptions = {'commit': True}

This will cause all instances of your fixture
to commit their objects after construction.

If you want to vary factory options between test cases
(eg if one test case requires the store to be commited,
but you don't want it to be the default)
you can supply factory options as keyword arguments
when calling ``Fixture.setup``, eg::

  self.f = MyFixture().setup(commit=True)

Or if you are using the context manager syntax 
you can supply factoryoptions in the fixture constructor, eg::

  with MyFixture(factoryoptions={'commit': True}) as fixturedata:
    ...

Accessing Storm's Store object
------------------------------

The store object is accessible via the factory's ``mapper`` attribute.
Use it to query existing objects in your fixtures::

	F = StormFactory.configure(...)

  	class MyFixture(Fixture):

		product = F.mapper.find(Product).any()
		order = F(Order, product_id=product.id, ...)

Note that ``mapper`` is a wrapper around the Store object
that defers evaluation of any calls
until the fixture objects are created.
You cannot use ``mapper``
to access the store object outside of fixture definitions.


Use with SQLAlchemy
-------------------

SQLAlchemy support is currently experimental. 
Much of the implementation is shared with ``StormFactory``,
as described above.
Please refer to this and the source code 
for usage instructions.

Other ORMs
----------

There is currently no support for other ORMs. Contributions are welcome!

Setup and teardown
------------------

Fixtures don't create any objects until you explicitly set them up::

    fixture = MyFixture()
    fixture.setup()

Fixtures will destroy any objects they've created when you call ``teardown``::

    fixture.teardown()

NB these methods are aliased to ``setUp`` and ``tearDown`` for consistency with
python's unittest library. 

Call these from your test classes' setup/teardown methods::


    class UserFixture(Fixture):
        user = Factory(User, username='fred')
        profile = Factory(Profile, user=user, address='10 Downing Street')

    class TestSuite:

        def setUp(self):
            self.fixtures = UserFixture()
            self.fixtures.setup()

        def tearDown(self):
            self.fixtures.teardown()

        def test_wotsit(self):
            assert self.fixtures.user.username == 'fred'
            assert self.fixtures.user.get_profile().address == \
              '10 Downing Street'


You can also use fixtures as context managers,
in which case setup and teardown will be called automatically 
when you enter/exit the block::

    with UserFixture() as f:
        assert f.user.username == 'fred'
        assert f.profile.address == '10 Downing Street'


Defining factories
------------------

The simplest approach is to create a new Factory for every object required::

    class MyFixture(Fixture):
        fred = Factory(User, username='fred', is_admin=False)
        albert = Factory(User, username='albert', is_admin=True)

You can avoid repeating code by predefine factories for commonly used model
classes::

    user_factory = Factory(User, is_admin=False, is_active=True)

    class MyFixture(Fixture):

        ursula = user_factory(username='ursula')
        inigo = user_factory(username='inigo')
        albert = user_factory(username='albert', is_admin=True)

Factories can reference other factories to autocreate related objects::

    company_factory = Factory(Company, name=Seq('megacorp-%d'))
    employee_factory = Factory(Employee, id=Seq(int), company=company_factory)

If ``employee_factory`` is called without a company argument,
it will generate a fresh one using ``company_factory``.

Sequences
---------

When creating multiple objects of the same type you can use the
``toffee.Seq`` class to avoid manually specifying unique values for
fields::

    product_factory = Factory(Product, sku=Seq('%04d', 0))

    class MyFixture(Fixture):
        p1 = product_factory()
        p2 = product_factory()
        p3 = product_factory()

This would assign ``p1.sku = '0000'``, ``p2.sku = '0001'``  and so on.

The first argument to Seq can be a string (eg ``'user-%d'``)
or any callable (eg ``int`` or ``lambda n: 'badger' * n``).
The second argument is the starting value
(default 0)


Object relationships and foreign keys
-------------------------------------

Suppose you have a bug tracking application. 
You might have one model object called ``Bug`` and another called ``Product`` 
– bugs always belong to a product.

How to set up a fixture containing a product with multiple bugs?

The simplest way is
to create all objects and link between them::

    class BugFixture(Fixture):

        product = Factory(Product, name='my amazing software')
        bug1 = Factory(Bug, comment="it doesnt work", product=product)
        bug2 = Factory(Bug, comment="it still doesnt work", product=product)

Now when we setup the fixture, toffee will figure out the relationships we need
to create the object graph - a single Product instance, linked to two bugs::

    with BugFixture() as f:
        assert f.bug1.product is f.product
        assert f.bug1.product is f.bug2.product


Suppose we write a lot of tests, and we need a lot of fixtures. To avoid having
to repeat a lot of code we can predefine the factories::

    product_factory = Factory(Product, name=Seq('Product-%d'))
    bug_factory = Factory(Bug, comment=Seq('Bug #%d'), product=product_factory)


Notice the ``product=product_factory`` bit. Using this ``bug_factory`` 
will call ``product_factory`` to generate a fresh product
for us every time::

    class BugsInSeparateProductsFixture(Fixture):

        bug1 = bug_factory()
        bug2 = bug_factory()

    with BugsInSeparateProductsFixture() as f:
        assert f.bug1.product.name == 'product-0'
        assert f.bug2.product.name == 'product-1'


If we want both bugs to link to a single product, we can just tell the second
bug to reuse the product from bug1::

    class BugsInSameProductFixture(Fixture):

        bug1 = bug_factory()
        bug1 = bug_factory(product=bug1.product)

    with BugsInSameProductFixture() as f:
        assert f.bug1.product.name == 'product-0'
        assert f.bug2.product.name == 'product-0'


Configuring subobjects
-----------------------

The double underscore syntax lets you specify attributes of child factories on
the parent. Suppose you have an factories for two different model classes::

    author_factory = Factory(Author, name=Seq('author-#%d'))
    book_factory = Factory(Book, name=Seq('book-%d'), author=author_factory())

Now you can write a fixture like this::

    class MyFixture(Fixture):

        player = book_factory(name='Animal Farm', author__name='Orwell')

Post-creation configuration
---------------------------

Override the ``configure`` method to add custom configuration of objects::

    class MyFixture(Fixture):

        user = userfactory()

        def configure(self):
            add_user_to_group('admin', self.user)



Extending fixtures
------------------

Class inheritance is the preferred way to extend fixtures::

    user_factory = Factory(User, username=Seq('user-%d'), is_admin=False)
        
    class UserFixture(Fixture):
        fred = user_factory()

    class UserWithAdministratorFixture(UserFixture):
        sheila = user_factory(is_admin=True)


But you can also extend fixtures in their constructor::

    with UserFixture(sheila=user_factory(is_admin=True)) as f:
        assert f.sheila.is_admin
        assert not f.fred.is_admin

