import shelve

olddbfile = 'studio.db'
newdbfile = 'newstudio.db'
dbkey = 'studio'

db = shelve.open(olddbfile)
studio = db[dbkey]
db.close()

for customer in studio.customers():
	customer.cell_phones = {}

db = shelve.open(newdbfile)
db[dbkey] = studio
db.close()

db = shelve.open(newdbfile)
studio = db[dbkey]
db.close()

print studio.show('s')
