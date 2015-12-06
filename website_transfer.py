import pymongo
import shelve
import re
import random
from management import *
from python_user_transfer.meteorUFO import *

def giveNames(name):
	arr = filter(None, re.compile('\s*').split(name))
	length = len(arr)
	if length == 1:
		arr.append('')
	if length == 0:
		arr.append('')
		arr.append('')
	if length > 2:
		return arr[0], arr[length - 1]

	return arr

def giveDate(date):
	return date.strftime('%m/%d/%Y')

def giveFloat(number):
	try: 
		number = float(number)
	except ValueError:
		print "Number was not a valid float: ", number
	return number

def giveMethod(method):
	return method

def giveComments(comments):
	return comments if not re.match('none', comments, flags = re.IGNORECASE) else ''

dbfile = 'studiodata/studio.db'
dbkey = 'studio'

studioshelf = shelve.open(dbfile)
studio = studioshelf[dbkey]
studioshelf.close()

db = pymongo.MongoClient().meteor
from pymongo.son_manipulator import SONManipulator
class ObjectIdManipulator(SONManipulator):
	def transform_incoming(self, son, collection):
		son[u'_id'] = str(son[u'_id'])		
		return son

db.add_son_manipulator(ObjectIdManipulator())

ufo = UFO()
ufo.orbit('mongodb://localhost:27017/meteor')

usersRemote = db.users
studentsRemote = db.students
lessonsRemote = db.lessons
paymentsRemote = db.payments
expensesRemote = db.expenses
studentExpensesRemote = db.studentexpenses


for customer in studio.customers:
	# Split and find the first and last names
	firstname, lastname = giveNames(customer.name)

	# Break apart the contact methods dictionary and push emails and phones.
	emails = []
	phones = []
	emailTest = re.compile('\S+@\S+\.\S+')
	phoneTest = re.compile('(\d{3}.)?\d{3}.\d{4}')
	for key, value in customer.contact_info.items():
		# if value matches email
		if re.match(emailTest, value):
			emails.append({'address': value, 'verified': False})
		# if value matches phone
		elif re.match(phoneTest, value):
			phones.append({'number': value, 'description': key})

	# Create password and either email or username
	password = '%010x' % random.randrange(16**10)
	if len(emails) == 0:
		email = (firstname + lastname).lower() + ('%04u' % random.randrange(10**4))
		byUserName = True
	else:
		email = emails[0]['address']
		byUserName = False
		if len(emails) > 1:
			emails = emails[1:]
		else:
			emails = []

	user = MeteorUser(email = email, password = password, byUserName = byUserName)
	ufo.beamDown(user)

	print firstname, lastname
	print email, password
	print

	userId = user.user[u'_id']
	usersRemote.update({'_id': userId},
		{ '$set': {'firstname': firstname, 'lastname': lastname, 'phones': phones}, '$push': {'emails': {'$each': emails}} })

	for student in customer.students:
		firstname, lastname = giveNames(student.name)
		price = giveFloat(student.price)
		inactive = not student.active

		studentId = studentsRemote.insert({'firstname': firstname, 'lastname': lastname, 'price': price})
		usersRemote.update({'_id': userId}, {'$push': {'student_ids': studentId}})

		for lesson in student.lessons:
			date = giveDate(lesson.date)
			price = giveFloat(lesson.price)
			comments = giveComments(lesson.comments)

			lessonId = lessonsRemote.insert({'date': date, 'price': price, 'comments': comments})
			studentsRemote.update({'_id': studentId}, {'$push': {'lesson_ids': lessonId}})

		for expense in student.expenses:
			date = giveDate(expense.date)
			price = giveFloat(expense.amount)
			comments = giveComments(expense.comments)

			expenseId = studentExpensesRemote.insert({'date': date, 'price': price, 'comments': comments})
			studentsRemote.update({'_id': studentId}, {'$push': {'expense_ids': expenseId}})

	for payment in customer.payments:
		date = giveDate(payment.date)
		amount = giveFloat(payment.amount)
		method = giveMethod(payment.method)
		comments = giveComments(payment.comments) 

		paymentId = paymentsRemote.insert({'date': date, 'amount': amount, 'method': method, 'comments': comments})
		usersRemote.update({'_id': userId}, {'$push': {'payment_ids': paymentId}})