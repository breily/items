Items
=====

* Items is a wrapper for parts of the SQLAlchemy library, originally written for
  Juno (http://github.com/breily/juno/).

* Homepage: http://brianreily.com/project/items


Usage
-----

    > import items
    > it = items.Items() # Creates 'sqlite:///:memory:'
    >
    > Person = it.model('Person', name='str')
    > brian = Person(name='brian')
    >
    > it.add(brian)
    > it.session.new
    IdentitySet([<Person: None>])
    > it.commit()
    > it.session.new
    IdentitySet([])
    >
    > it.find(Person).all()
    [<Person: 1>]
    > it.find(Person).all()[0].name
    u'brian'

