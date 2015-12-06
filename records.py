# Offset is a number representing how many days in the past this occurred.
class Record(object):

	def __init__(self, comments, offset):
		self.date = give_date_from_offset(offset)
		self.comments = comments

	def __str__(self):
		return s("%s: %s", dat(self.date), self.comments)

	def change(self, attr, value):
		if attr not in ['date', 'comments']:
			return
		if attr == 'comments':
			self.comments = value
		elif attr == 'date':
			self.date = give_date_from_offset(value)

class Lesson(Record):

	def __init__(self, comments, offset, price):
		self.price = float(price)
		super(Lesson, self).__init__(comments, offset)

	def __str__(self):
		return s("%s: $%.2f, Comments: %s", dat(self.date), self.price, self.comments)

	def output(self):
		return s("%s\t$%.2f\t%s", dat(self.date), self.price, self.comments)

	def change(self, attr, value):
		super(Lesson, self).change(attr, value)
		if attr in ['price']:
			setattr(self, attr, float(value))

# Expenses, Contacts, Payments, which are all Records.	
class Expense(Record):

	def __init__(self, amount, comments, offset):
		self.amount = float(amount)
		super(Expense, self).__init__(comments, offset)

	def __str__(self):
		return s("%s: $%.2f, %s", dat(self.date), self.amount, self.comments)

	def output(self):
		return s("%s\t$%.2f\t%s", dat(self.date), self.amount, self.comments)

	def change(self, attr, value):
		super(Expense, self).change(attr, value)
		if attr == 'amount':
			self.amount = float(value)

class Payment(Record):

	def __init__(self, amount, method, comments, offset):
		self.amount = float(amount)
		self.method = cap(method)
		super(Payment, self).__init__(comments, offset)

	def __str__(self):
		return s("%s: $%.2f, Method: %s, %s", dat(self.date), self.amount, self.method, self.comments)

	def output(self):
		return s("%s\t$%.2f\t%s\t%s", dat(self.date), self.amount, self.method, self.comments)

	def change(self, attr, value):
		super(Payment, self).change(attr, value)
		if attr == 'amount':
			self.amount = float(value)
		elif attr == 'method':
			self.method = value

class Contact(Record):

	def __init__(self, from_me, resolved, comments, offset):
		self.from_me = from_me
		self.resolved = resolved
		super(Contact, self).__init__(comments, offset)

	def __str__(self):
		return s("%s: %s, %s: %s", dat(self.date), "From Me" if self.from_me else "From Them",  "Resolved" if self.resolved else "Unresolved", self.comments)

	def output(self):
		return s("%s\t%s\t%s\t%s", dat(self.date), "From Me" if self.from_me else "From Them",  "Resolved" if self.resolved else "Unresolved", self.comments)

	def change(self, attr, value):
		super(Contact, self).change(attr, value)
		if attr in ['from_me', 'resolved']:
			setattr(self, attr, mybool(value))

 # Random static methods.

def give_date_from_offset(offset):
	try:
		a = int(offset)
		import datetime
		return datetime.datetime.today() - datetime.timedelta(days = a)
	except ValueError:
		import datetime
		return datetime.datetime.strptime(offset, '%m/%d/%Y')

def s(string, *args):
	return string % args

def mybool(string):
	if type(string) == str:
		return 'true' == string.lower() or string.lower() in 'true'
	else:
		return string

def cap(string):
	return ' '.join(word.capitalize() for word in string.split())

def dat(date):
	return date.strftime('%m/%d/%Y') if date else date

def is_time(string):
	import re
	return bool(re.match("^1[0-2]|[1-9]\.?([0-6][0-9]?)?$", string))