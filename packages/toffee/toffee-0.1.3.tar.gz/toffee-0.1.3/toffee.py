from itertools import count

__version__ = '0.1.3'


class BaseFactory(object):

    created_order = 0

    def create_object(self, context):
        raise NotImplementedError()

    def destroy_object(self, context, ob):
        raise NotImplementedError()

    @classmethod
    def configure(cls):
        """\
        Return a dynamically created Factory subclass.

        In the Factory base class this serves no functional purpose, however
        subclasses may extend this to provide configuration points.
        For example :class:`~toffee.StormFactory` uses this to allow the user
        to supply the getstore method.
        """
        return type(cls.__name__, (cls,), {})

    @classmethod
    def setup_complete(self, context, created):
        """\
        Override this in subclasses to implement custom behaviour after all
        objects have been created (eg flushing to database)
        """

    @classmethod
    def teardown_complete(self, context, created):
        """\
        Override this in subclasses to implement custom behaviour after all
        objects have been torn down (eg flushing to database)
        """


class Factory(BaseFactory):

    _creation_order = count()

    def __init__(self, what, *args, **kwargs):

        for name in ['configure_object', 'create_object', 'destroy_object']:
            meth = kwargs.pop(name, None)
            if meth is not None:
                setattr(self, '_' + name, meth)

        self.what = what
        self.args = args
        self.kwargs = AttrDict(kwargs)
        self.created_order = next(self._creation_order)

        # process subfactory__attribute='foo'
        for k, v in list(self.kwargs.items()):
            if '__' in k:
                head, tail = k.split('__', 1)
                self.kwargs[head] = self.kwargs[head](**{tail: v})
                del self.kwargs[k]

    def __getitem__(self, attr):
        return LazyRecorderFactory(self)[attr]

    def __getattr__(self, attr):
        return getattr(LazyRecorderFactory(self), attr)

    def __setitem__(self, attr, value):
        if '.' in attr:
            head, tail = attr.split('.', 1)
            self.kwargs[head] = self.kwargs[head](**{tail: value})
        else:
            self.kwargs[attr] = value

    def __call__(self, *args, **kwargs):
        return self.__class__(self.what,
                              *(args or self.args),
                              **dict(self.kwargs, **kwargs))

    def __get__(self, instance, context):
        """
        Factories have magic behaviour in the context of fixtures, so that
        accessing 'my_fixture.foo' auto-delegates to 'my_fixture.o.foo'
        """
        if isinstance(instance, Fixture):
            try:
                return instance.o[instance.factory_names[self]]
            except KeyError:
                raise AttributeError()
        return self

    def create_object(self, context):
        args = tuple(context.resolve(a) for a in self.args)
        kwargs = dict((k, context.resolve(v)) for k, v in self.kwargs.items())

        ob = self._create_object(context, args, kwargs)
        ob = self._configure_object(ob, context)
        return ob

    def destroy_object(self, context, ob):
        return self._destroy_object(context, ob)

    def _create_object(self, context, args, kwargs):
        return self.what(*args, **kwargs)

    def _destroy_object(self, context, ob):
        pass

    def _configure_object(self, ob, context):
        return ob


class CallFactory(Factory):
    """\
    A factory that returns the value of a callable function or object.

    Use this to lazily instantiate values that are accessible at setup
    time but not necessarily earlier::

        class fixture(Fixture):

            user = CallFactory(lambda: User.objects.get(username='admin'))
            ...

    """

    def _create_object(self, context, args, kwargs):
        return self.what(*args, **kwargs)

    def _destroy_object(self, context, ob):
        pass


class LazyRecorder(object):
    """
    Records all calls and attribute access for later replay, eg:

        >>> p = LazyRecorder().upper().replace('c', 'm')[0]
        >>> p.replay('cat')
        'M'
    """

    def __init__(self):
        self._recorded_events = []

    def __call__(self, *args, **kwargs):
        self._recorded_events.append(lambda ob: ob(*args, **kwargs))
        return self

    def __getattr__(self, attr):
        self._recorded_events.append(lambda ob: getattr(ob, attr))
        return self

    def __getitem__(self, item):
        self._recorded_events.append(lambda ob: ob[item])
        return self

    def replay_with(self, ob):
        for event in self._recorded_events:
            ob = event(ob)
        return ob


class LazyRecorderFactory(BaseFactory, LazyRecorder):
    """
    Wraps a factory to record any calls/attribute access
    """
    def __init__(self, factory):
        LazyRecorder.__init__(self)
        BaseFactory.__init__(self)
        self.factory = factory
        self.created_order = factory.created_order

    def create_object(self, context):
        return self.factory.create_object(context)

    def destroy_object(self, context, ob):
        return self.factory.destroy_object(ob)


class DjangoFactory(Factory):

    def _create_object(self, context, args, kwargs):
        ob = self.what.objects.create(*args, **kwargs)
        ob.save()
        return ob

    def _destroy_object(self, context, ob):
        ob.delete()


class _DataMapperFactory(Factory):
    """\
    A factory that requires a data mapper object (eg a storm store or
    sqlalchemy session) in order to bind objects to the database.
    """

    #: Callable that returns the data mapper object
    _getmapper = lambda: None
    mapperkey = '_datamapper'

    default_flush = True
    default_commit = False

    @classmethod
    def _mapper_flush(cls, context):
        mapper = cls._getmapper_cached(context)
        if mapper is not None:
            mapper.flush()

    @classmethod
    def _mapper_commit(cls, context):
        mapper = cls._getmapper_cached(context)
        if mapper is not None:
            mapper.commit()

    def _mapper_add(self, context, ob):
        """
        Ask the datamapper to add ``ob`` to the data store
        """
        mapper = self._getmapper_cached(context)
        if mapper is not None:
            mapper.add(ob)

    def _mapper_remove(self, context, ob):
        """
        Ask the datamapper to remove ``ob`` from the data store
        """
        mapper = self._getmapper_cached(context)
        if mapper is not None:
            mapper.remove(ob)

    @classmethod
    def configure(cls, getmapper, *args, **kwargs):
        classob = super(_DataMapperFactory, cls).configure(*args, **kwargs)
        classob = type(cls.__name__, (classob,),
                       {'_getmapper': staticmethod(getmapper)})

        class MapperAccessFactory(classob):
            """
            Give direct access to the mapper object when creating fixtures,
            eg::

                class fixture(Fixture):
                    user = StormFactory.mapper.find(User, User.id == 1).one()
            """

            def __init__(self):
                super(MapperAccessFactory, self).__init__(None)

            def create_object(self, context):
                return self._getmapper_cached(context)

            def destroy_object(self, context, ob):
                pass

        classob.mapper = MapperAccessFactory()
        return classob

    @classmethod
    def _getmapper_cached(cls, context):
        try:
            return context.factoryoptions[cls.mapperkey]
        except KeyError:
            return context.factoryoptions.setdefault(cls.mapperkey,
                                                     cls._getmapper())

    @classmethod
    def setup_complete(cls, context, created):
        if context.factoryoptions.get('flush', cls.default_flush):
            cls._mapper_flush(context)
        if context.factoryoptions.get('commit', cls.default_commit):
            cls._mapper_commit(context)

    @classmethod
    def teardown_complete(cls, context, created):
        if context.factoryoptions.get('flush', cls.default_flush):
            cls._mapper_flush(context)
        if context.factoryoptions.get('commit', cls.default_commit):
            cls._mapper_commit(context)

    def _create_object(self, context, args, kwargs):
        ob = self.what.__new__(self.what)
        for item, value in kwargs.items():
            setattr(ob, item, value)
        self._mapper_add(context, ob)
        return ob

    def _destroy_object(self, context, ob):
        self._mapper_remove(context, ob)


class StormFactory(_DataMapperFactory):
    """\
    Typically you will need to configure this at the start of your test code,
    like so::

        getstore = lamdba: getUtility(IZStorm).get('main'))
        Factory = StormFactory.configure(getstore)

    You can then use Factory as normal::

        class fixture(Fixture):
            user = Factory(models.User, ...)

    By default, StormFactory calls ``store.flush`` but not ``store.commit``.
    Change this behaviour by passing factory options to setup::

        fixture.setup(flush=False)
        fixture.setup(commit=True)

    Alternatively you can supply factory options in the fixture class:

        class fixture(Fixture):
            factoryoptions = {'commit': True}

    """


class SQLAlchemyFactory(_DataMapperFactory):
    """\

    Typically you will need to configure this at the start of your test code,
    like so::

        Session = sessionmaker(...)
        Factory = SQLAlchemyFactory.configure(Session)

    You can then use Factory as normal::

        class fixture(Fixture):
            user = Factory(models.User, ...)

    By default, SQLAlchemyFactory calls ``session.flush`` but not
    ``session.commit``.
    Change this behaviour by passing factory options to setup::

        fixture.setup(flush=False)
        fixture.setup(commit=True)

    Alternatively you can supply factory options in the fixture class:

        class fixture(Fixture):
            factoryoptions = {'commit': True}

    """

    def _mapper_remove(self, context, ob):
        """
        Ask the datamapper to remove ``ob`` from the data store
        """
        mapper = self._getmapper_cached(context)
        if mapper is not None:
            mapper.delete(ob)

    def _create_object(self, context, args, kwargs):
        from sqlalchemy.orm.attributes import manager_of_class
        ob = manager_of_class(self.what).new_instance()
        for item, value in kwargs.items():
            setattr(ob, item, value)
        self._mapper_add(context, ob)
        return ob


class ArgumentGenerator(object):
    """
    A callable that dynamically generates factory arguments
    """

    def __init__(self, fn):
        self.fn = fn

    def __call__(self):
        return self.fn()


class ArgumentGeneratorFactory(object):
    """
    A factory for producing ``ArgumentGenerator`` objects.

    For an example, see :class:`~toffee.Seq`
    """

    def make_argument_generator(self):
        raise NotImplementedError


class Seq(ArgumentGeneratorFactory):

    def __init__(self, str_or_fn='%d', start=0):
        self.str_or_fn = str_or_fn
        self.start = start

    def make_argument_generator(self):
        counter = count(self.start)

        def seq():
            n = next(counter)
            if callable(self.str_or_fn):
                return self.str_or_fn(n)
            else:
                return self.str_or_fn % (n,)
        return ArgumentGenerator(seq)


class AttrDict(dict):

    def __getattr__(self, item):
        return self[item]

    def __setattr__(self, item, value):
        self[item] = value


class Fixture(object):

    #: Default factory options. See :class:`~toffee.StormFactory` for an
    #: example of how these are used to control flush and commit options.
    factoryoptions = {}

    def __init__(self, **kwargs):

        #: Factory definitions
        self.d = AttrDict()
        self.factory_names = {}

        #: Factory-created objects
        self.o = AttrDict()
        self.created = None

        self.factoryoptions_defaults = self.factoryoptions.copy()
        self.factoryoptions_defaults.update(kwargs.pop('factoryoptions', {}))

        class_factories = ((k, getattr(self.__class__, k))
                           for k in dir(self.__class__))
        class_factories = ((k, v)
                           for k, v in class_factories
                           if isinstance(v, Factory))

        self.update_factories(dict(class_factories, **kwargs))

    def __getattr__(self, name):
        try:
            return self.o[name]
        except KeyError:
            raise AttributeError(name)

    def update_factories(self, factories):
        for k, v in factories.items():
            if v in self.factory_names:
                raise ValueError("Factory %r used more than once (%r and %r)" %
                                 (v, k, self.factory_names[v]))
            self.factory_names[v] = k
        self.d.update(factories)

    def setup(self, force=False, **factoryoptions):
        """
        :param force: allow calls to setup to be nested
        :param **factoryoptions: any factory specific options, for example
                                 passing flags such as ``commit=True``. See
                                 individual factory subclasses for information
        """
        if self.created and not force:
            raise Exception("setup() has already been called on this fixture. "
                            "Call teardown first, or use setup(force=True).")

        self.factoryoptions = dict(self.factoryoptions_defaults,
                                   **factoryoptions)
        self.o = AttrDict()
        self.created = []
        self.argument_generators = {}

        factories = sorted((v.created_order, k) for k, v in self.d.items())
        for _, name in factories:
            self._get_or_create_named_object(name)
        self.setup_complete()
        return self

    def setup_complete(self):
        """\
        Call any setup_complete methods on factory classes to let them know
        that all objects have been created
        """
        factory_created = {}

        for name, ob, factory in self.created:
            factory_created.setdefault(factory.__class__, []).append(ob)

        for f, obs in factory_created.items():
            f.setup_complete(self, obs)

        self.configure()

    def teardown_complete(self, torndown):
        """\
        Call any teardown_complete methods on factory classes to let them know
        that all objects have been torn down
        """
        factory_created = {}

        for name, ob, factory in torndown:
            factory_created.setdefault(factory.__class__, []).append(ob)

        for f, obs in factory_created.items():
            f.teardown_complete(self, obs)

    def configure(self):
        """\
        Subclasses should override this to provide custom post-creation
        configuration
        """

    def _get_or_create_named_object(self, name):
        """\
        Return the object from the named factory, creating it if necessary
        """
        try:
            return self.o[name]
        except KeyError:
            pass
        return self._create_object_from_factory(self.d[name])

    def _create_object_from_factory(self, factory):
        """\
        Invoke ``factory`` to create and configure an object.
        Register the created object so that it may later be referenced and
        torn down.
        """
        name = self.factory_names.get(factory, None)
        ob = factory.create_object(self)
        self.created.append((name, ob, factory))

        if isinstance(factory, LazyRecorderFactory):
            ob = factory.replay_with(ob)

        if name is not None:
            self.o[name] = ob
        return ob

    def resolve(self, what):

        if isinstance(what, ArgumentGeneratorFactory):
            if what not in self.argument_generators:
                self.argument_generators[what] = \
                        what.make_argument_generator()
            return self.argument_generators[what]()

        if isinstance(what, ArgumentGenerator):
            return what()

        if isinstance(what, Factory):
            return self.resolve(LazyRecorderFactory(what))

        if isinstance(what, LazyRecorderFactory):
            if what.factory in self.factory_names:
                name = self.factory_names[what.factory]
                ob = self._get_or_create_named_object(name)
            else:
                ob = self._create_object_from_factory(what.factory)

            return what.replay_with(ob)

        return what

    def teardown(self):
        torndown = []
        while self.created:
            name, ob, factory = self.created.pop()
            if name is not None:
                del self.o[name]
            factory.destroy_object(self, ob)
            torndown.append((name, ob, factory))
        self.teardown_complete(torndown)
        self.factoryoptions = {}

    def __enter__(self):
        return self.setup()

    def __exit__(self, type, value, tb):
        if type:
            try:
                self.teardown()
            except Exception:
                pass
        else:
            self.teardown()
        return False

    #: Alias for compatility with unittest names
    setUp = setup

    #: Alias for compatility with unittest names
    tearDown = teardown
