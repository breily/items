Items
=====

* Items is a wrapper for parts of the SQLAlchemy library, originally written for
  Juno (http://github.com/breily/juno/).

* Specifically, it wraps the database setup and class/table creation portions.

* Homepage: http://brianreily.com/project/items


Example Usage
-------------

    import items
    it = items.Items() # Creates 'sqlite:///:memory:'
    
    Person = it.model('Person', name='str')
    brian = Person(name='brian')
     
    it.add(brian)
    it.session.new
    => IdentitySet([<Person: None>])
    it.commit()
    it.session.new
    => IdentitySet([])
     
    it.find(Person).all()
    => [<Person: 1>]
    it.find(Person).all()[0].name
    => u'brian'


Details
-------

* First, create an Items object.  This takes two optional arguments:
    
      engine_type     => By default, 'sqlite'
      engine_location => By default, ':memory:'

  See http://sqlalchemy.org/docs/05/dbengine.html for details.

  In 'driver://username:password@host:port/database', driver would be the
  engine_type argument.  Everything after (except for the '://') is the
  engine_location argument.

* Use your items object to create classes, with model().  model() takes 
  three types of arguments:
    
      model_name   => The name of your new class (technically it does not have
                      to be the same name, but this makes the most sense).
      column types => Any variables you want your class to have.  In the 
                      above example, 'name' is a variable and 'str' is the 
                      column type.  See <items.column_mapping> for options.
      callables    => Any functions you want your class to have.

* Models come built with an __init__ function and a __repr__ function.  Any
  others you want you have to give to the constructor:
    
      Person = it.model('Person', i='int', double=lambda self, x: x * 2)
      p = Person(i=4)
      p.double(17)
      => 34

* To access the database, your Items object includes a number of methods:
    
      it.find(Person)  => Returns a SQLAlchemy query object.
      it.add(instance) => Add an instance (or multiple instances) to the current 
                          session.
      it.commit()      => Commit any pending changes.

* You can also use the session object to do these things directly:
    
      it.session       => Return a SQLAlchemy session object.


