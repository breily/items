import items

it = items.Items('sqlite:///:memory:') # This is the default

Book = it.model('Book', name='string', author='string', length='int')

hhgtg = Book(name="Hitchhiker's Guide", author="Adams",    length=487)
fc    = Book(name="Fight Club",         author="Chuck P.", length=213)

it.add(hhgtg)
it.commit()

fc.save()

print "My Books: "
for b in Book.all():
    print "\t%s by %s (%s pages)" % (b.name, b.author, b.length)

print "Filtered List: "
for b in Book.filter(Book.name.like("Fight%")):
    print "\t%s by %s (%s pages)" % (b.name, b.author, b.length)
