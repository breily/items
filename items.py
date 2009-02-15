from sqlalchemy import (create_engine, Table, MetaData, Column, Integer, String,
                        Unicode, Text, UnicodeText, Date, Numeric, Time, Float,
                        DateTime, Interval, Binary, Boolean, PickleType)
from sqlalchemy.orm import sessionmaker, mapper

class ModelError(Exception): pass

class Items(object):
    def __init__(self, engine_name='sqlite:///:memory:'):    
        self.engine = create_engine(engine_name)
        self.session = sessionmaker(bind=self.engine)()
        self.models = {}

    def model(self, model_name, **kwargs):
        # Start building the __dict__ for the class
        # These functions defined below
        cls_dict = {'__init__': init_func,
                    '__name__': model_name,
                    '__repr__': repr_func,
                    'save':     save_func,
                    'session':  self.session,
                    'hub':      self,
                    # Static methods
                    '__self__': None,
                    'find':     None,
                    # Static Query object methods
                    'all':       None,
                    'count':     None,
                    'filter':    None,
                    'filter_by': None,
                    'first':     None,
                   }
        # Automatically include an 'id' column
        cols = [ Column('id', Integer, primary_key=True), ]
        # Parse kwargs to get column definitions and class functions
        for k, v in kwargs.items():
            # Allow users to include their own columns
            if isinstance(v, Column):
                if not v.name: v.name = k
                cols.append(v)
            # These would be functions - we just add them to the __dict__
            elif callable(v):
                cls_dict[k] = v
            # These would be column types - we add a corresponding SQLAlchemy column
            elif type(v) == str:
                v = v.lower()
                if v in column_mapping: v = column_mapping[v]
                else: raise ModelError("'%s' is not an allowed database column" %v)
                cols.append(Column(k, v))
        if len(cols) == 1:
            raise ModelError("Must have at least one column other than id")
        # Create the class
        new_model = ModelConstructor(model_name, (object,), cls_dict)
        # Wrap the find function in a lambda so that we can pass in the class
        # now, instead of needing to do that later.  Make sure the lambda
        # becomes a staticmethod so we can do Person.find(), instead of p.find()
        new_model.__self__  = new_model
        new_model.find      = staticmethod(lambda: find_func(new_model))
        new_model.all       = staticmethod(lambda: all_func(new_model))
        new_model.count     = staticmethod(lambda: count_func(new_model))
        new_model.first     = staticmethod(lambda: first_func(new_model))
        new_model.filter    = staticmethod(lambda criterion: filter_func(new_model, criterion))
        new_model.filter_by = staticmethod(lambda **kwargs: filter_by_func(new_model, **kwargs))
        # Hopefully replace all of that with __getattribute__
        #new_model.__getattribute__ = staticmethod(lambda attr: attr_func(new_model, attr))
        #new_model.__getattr__ = staticmethod(lambda attr: attr_func(new_model, attr))

        # Setup the table
        metadata = MetaData()
        new_table = Table(model_name + 's', metadata, *cols)
        metadata.create_all(self.engine)
        # Map the table to the created class
        mapper(new_model, new_table)
        # Record the model, create find function, and return the class
        self.models[model_name] = new_model
        return new_model

    def find(self, model_cls):
        if type(model_cls) == str:
            try: model_cls = self.models[model_cls]
            except: raise NameError("That model ('%s') does not exist" %model_cls)
        return self.session.query(model_cls)

    def add(self, *args):
        self.session.add_all(args)

    def commit(self):
        self.session.commit()

class ModelConstructor(type):
    """Metaclass to return another class."""
    def __new__(cls, name, bases, dct):
        return type.__new__(cls, name, bases, dct)
    def __init__(cls, name, bases, dct):
        super(ModelConstructor, cls).__init__(name, bases, dct)

# Map SQLAlchemy's types to string versions of them for convenience
column_mapping = {'string':      String,      'str':      String,
                  'integer':     Integer,     'int':      Integer, 
                  'unicode':     Unicode,     'text':     Text,
                  'unicodetext': UnicodeText, 'date':     Date,
                  'numeric':     Numeric,     'time':     Time,
                  'float':       Float,       'datetime': DateTime,
                  'interval':    Interval,    'binary':   Binary,
                  'boolean':     Boolean,     'bool':     Boolean,
                  'pickletype':  PickleType,
                 }

#
# Functions added to created classes
#

# Generic __init__ to set instance variables of a class.
def init_func(self, **kwargs):
    for key, val in kwargs.items(): self.__dict__[key] = val

# Generic __repr__ to print the class name and database id
def repr_func(self):
    return '<%s: %s>' %(self.__name__, self.id)

# Add and commit and instance to the session
def save_func(self):
    self.session.add(self)
    self.session.commit()
    return self

### Query functions

def find_func(cls): return cls.session.query(cls)

# Hopefully listing all is will be unnecessary and I'll be able to 
# automatically pass them to query().
def all_func(cls):                 return cls.session.query(cls).all()
def count_func(cls):               return cls.session.query(cls).count()
def first_func(cls):               return cls.session.query(cls).first()
def filter_func(cls, criterion):   return cls.session.query(cls).filter(criterion)
def filter_by_func(cls, **kwargs): return cls.session.query(cls).filter_by(**kwargs)

# Code below in progress, not currently used

def attr_func(self, attr):
    if attr in ['__name__', '__repr__', '__init__']:
        return object.__getattribute__(attr)
    q = self.find()
    print 'self: %s' %self
    print 'attr: %s' %attr
    print 'q: %s' %q
    return q.__getattribute__(attr)
    #return lambda: q.__getattribute__(attr)

"""
Maybe make the model into the session?
    Book.add(a, b, c)
    Book.commit()
    Book.all()
    Book.filter(Book.name.like="Fight%")

Then get rid of the Items controller.

Notes:
    Book.__getattribute__('all')() works
    Book.all() does not
"""
