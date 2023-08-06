
import functools
from collections import namedtuple

import sqlalchemy
from sqlalchemy import inspect, orm, and_, or_
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta
from sqlalchemy.orm.exc import UnmappedClassError

import query
from utils import classproperty, is_sequence, has_primary_key, camelcase_to_underscore

Event = namedtuple('Event', ['name', 'listener', 'kargs'])

class ModelMeta(DeclarativeMeta):
    def __new__(cls, name, bases, dict_):
        # set __tablename__ (if not defined) to underscore version of class name
        if not dict_.get('__tablename__') and not dict_.get('__table__') is not None and has_primary_key(dict_):
            dict_['__tablename__'] = camelcase_to_underscore(name)

        # set __events__ to expected default so that it's updatable when initializing
        # e.g. if class definition sets __events__=None but defines decorated events,
        # then we want the final __events__ attribute to reflect the registered events.
        # if set to anything that's non-empty/non-dict will lead to an error if decorated events defined
        if not dict_.get('__events__'):
            dict_['__events__'] = {}

        return DeclarativeMeta.__new__(cls, name, bases, dict_)

    def __init__(cls, name, bases, dict_):
        events = []

        # append class attribute defined events
        if dict_.get('__events__'):
            # events defined on __events__ can have many forms (e.g. string based, list of tuples, etc)
            # so we need to iterate over them and parse into standardized Event object
            for event_name, listeners in dict_['__events__'].iteritems():
                if not isinstance(listeners, list):
                    listeners = [listeners]

                for listener in listeners:
                    if isinstance(listener, tuple):
                        # listener definition includes event.listen keyword args
                        listener, kargs = listener
                    else:
                        kargs = {}

                    if not hasattr(listener, '__call__'):
                        # no __call__ attribute? then assume listener is a string reference to class method
                        listener = dict_[listener]

                    events.append(Event(event_name, listener, kargs))

        # append events which were added via @event decorator
        events += [value.__event__ for value in dict_.values() if hasattr(value, '__event__')]

        if events:
            # reassemble events dict into consistent form using Event objects as values
            events_dict = {}
            for event in events:
                sqlalchemy.event.listen(cls, event.name, event.listener, **event.kargs)
                events_dict.setdefault(event.name, []).append(event)

            dict_['__events__'].update(events_dict)

        super(ModelMeta, cls).__init__(name, bases, dict_)


class ModelBase(object):
    '''Augmentable Base class for adding shared model properties/functions'''

    # default table args
    __table_args__ = {}

    # define a default order by when not specified by query operation
    # eg: { 'order_by': [column1, column2] }
    __mapper_args__ = {}

    # register orm event listeners
    __events__ = {}

    # query class to use for self.query
    query_class = query.Query

    # an instance of `query_class`
    # can be used to query the database for instances of this model
    # @note: requires setting Class.query = QueryProperty(session) when session available
    # see `make_declarative_base()` for automatic implementation
    query = None

    # specify sqla.session.query.filter() options for advanced and simple searches
    # eg: { key: lambda value: Model.column_name == val }
    __advanced_search__ = {}
    __simple_search__ = {}

    def __init__(self, *args, **kargs):
        self.update(*args, **kargs)

    def __repr__(self):
        '''
        Default representation of model
        '''
        values = ', '.join(['{0}={1}'.format(c, repr(getattr(self, c))) for c in self.columns])
        return '<{0}({1})>'.format(self.__class__.__name__, values)

    def update(self, data_dict=None, strict=False, **kargs):
        '''
        Update model with arbitrary set of data
        '''

        data = data_dict if isinstance(data_dict, dict) else kargs

        updatable_fields = self.strict_update_fields if strict else data.keys()
        relationships = self.relationships

        for k,v in data.iteritems():
            if hasattr(self, k) and k in updatable_fields:
                # consider v a dict if any of its elements are a dict
                v_is_dict = any([isinstance(_v, dict) for _v in v]) if is_sequence(v) else isinstance(v, dict)

                attr = getattr(self, k)

                if hasattr(attr, 'update') and v_is_dict:
                    # nest calls to attr.update if available and input is a data dict
                    attr.update(v)
                else:
                    if k in relationships and v_is_dict and not v:
                        # typically, if v is {}, then we're usually updating a relationship attribute
                        # where the relationship has an empty/null value in the database
                        # (e.g. a frontend sends missing relationship attribute as {})
                        # but if we set a relationship attribute = {}, things blow up
                        # so instead, convert {} to None which is valid for standard relationship attribute
                        v = None
                    setattr(self, k, v)

    def to_dict(self):
        '''
        Return dict representation of model.

        Drill down to any relationships and serialize those too.

        Assume that the current object has been loaded (lazy/joined/etc)
        and don't try to expand anything, i.e., just serialize the currently loaded data
        '''
        d = {}

        for field, value in self.__dict__.iteritems():
            if field.startswith('_sa'):
                # skip sqlalchemy properties
                continue

            d[field] = [v.to_dict() for v in value] if is_sequence(value) else value

        return d

    @property
    def strict_update_fields(self):
        '''
        Model fields which are allowed to be updated during strict mode

        Default is to limit to table columns
        Override as needed in child classes
        '''
        return self.columns

    ##
    # search/filtering methods
    ##

    @classmethod
    def get_search(cls, search_dict, filter_fns):
        filters = []

        for key, filter_fn in [(k,v) for k,v in filter_fns.iteritems() if k in search_dict]:
            filters.append(filter_fn(search_dict[key]))

        return filters

    @classmethod
    def advanced_search(cls, search_dict):
        filters = None
        if cls.__advanced_search__:
            _filters = cls.get_search(search_dict, cls.__advanced_search__)

            if _filters:
                filters = and_(*_filters)

        return filters

    @classmethod
    def simple_search(cls, search_string):
        filters = None

        if cls.__simple_search__:
            terms = [s for s in search_string.split()]
            fields = cls.__simple_search__.keys()
            field_count = len(fields)

            search_filters = []

            for term in terms:
                # create a dict with each `config_search` key and `term` so filters can be applied to each combination
                # i.e. { config_search_key1: term, config_search_key2: term, ..., config_search_keyN, term }
                search_dict = dict(zip(fields, [term]*field_count))
                term_filters = cls.get_search(search_dict, cls.__simple_search__)

                if term_filters:
                    # `or` filters together since only 1 filter needs to match for `term`
                    search_filters.append(or_(*term_filters))

            if search_filters:
                # `and` all search conditions together
                # each `term` should have an OR'd set of filters that evaluates to True
                filters = and_(*search_filters)

        return filters

    ##
    # session based methods/properties
    ##

    @property
    def session(self):
        '''Return session belonging to self'''
        return orm.object_session(self)

    def flush(self, *args, **kargs):
        return self.session.flush([self], *args, **kargs)

    def delete(self, *args, **kargs):
        return self.session.delete(self, *args, **kargs)

    def expire(self, *args, **kargs):
        return self.session.expire(self, *args, **kargs)

    def refresh(self, *args, **kargs):
        return self.session.refresh(self, *args, **kargs)

    def expunge(self, *args, **kargs):
        return self.session.expunge(self, *args, **kargs)

    @classmethod
    def get(cls, *args, **kargs):
        return cls.query.get(*args, **kargs)

    ##
    # inspect based methods/properties
    ##

    @classproperty
    def attrs(cls):
        '''Return ORM attributes'''
        return inspect(cls).attrs.keys()

    @classproperty
    def descriptors(cls):
        '''Return all ORM descriptors'''
        return [d for d in inspect(cls).mapper.all_orm_descriptors.keys() if not d.startswith('__')]

    @classproperty
    def relationships(cls):
        '''Return ORM relationships'''
        return inspect(cls).mapper.relationships.keys()

    @classproperty
    def column_attrs(cls):
        '''Return table columns as list of class attributes at the class level'''
        return inspect(cls).mapper.column_attrs

    @classproperty
    def columns(cls):
        '''Return table columns'''
        return inspect(cls).mapper.columns.keys()

class QueryProperty(object):
    def __init__(self, session):
        self.session = session

    def __get__(self, model, Model):
        try:
            mapper = orm.class_mapper(Model)
            if mapper:
                if not getattr(Model, 'query_class', None):
                    Model.query_class = query.Query

                q = Model.query_class(mapper, session=self.session())
                q.__model__ = Model

                return q
        except UnmappedClassError:
            return None

def make_declarative_base(session=None, query_property=None, Model=None):
    Model = Model or declarative_base(cls=ModelBase, constructor=ModelBase.__init__, metaclass=ModelMeta)
    extend_declarative_base(Model, session, query_property)
    return Model

def extend_declarative_base(Model, session=None, query_property=None):
    # attach query attribute to Model if `session` object passed in
    if session:
        Model.query = query_property(session) if query_property else QueryProperty(session)

def event(event_name, **kargs):
    def _event(f, *args, **kargs):
        f.__event__ = Event(event_name, f, kargs)

        @functools.wraps(f)
        def wrapper(cls, *args, **kargs):
            return f(*args, **kargs)

        return wrapper

    return _event

