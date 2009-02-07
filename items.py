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
                    '__repr__': repr_func 
                   }
        # Automatically include an 'id' column
        cols = [ Column('id', Integer, primary_key=True), ]
        # Parse kwargs to get column definitions and class functions
        for k, v in kwargs.items():
            # These would be functions - we just add them to the __dict__
            if callable(v):
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
    for key, val in kwargs.items():
        self.__dict__[key] = val

# Generic __repr__ to print the class name and database id
def repr_func(self):
    return '<%s: %s>' %(self.__name__, self.id)

