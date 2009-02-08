import items

it = items.Items('sqlite:///:memory:')

Book = it.model('Book', name='string', author='string', length='int')

hhgtg = Book(name="Hitchhiker's Guide", author="Adams", length=487)
fc = Book(name="Fight Club", author="Chuck P.", length=213)

it.add(hhgtg, fc)
it.commit()

print "My Books: "
for b in it.find(Book).all():
    print "\t%s by %s (%s pages)" %(b.name, b.author, b.length)
