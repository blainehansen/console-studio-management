from records import *
from output_strings import *
import subprocess

class Studio(object):

	def __init__(self):
		self.customers = []
		self.expenses = []

	def find(self, customer_student, name):
		char = customer_student[0]
		if char == 'c':
			array = self.customers
		elif char == 's':
			array = self.gather_students()
		else:
			return "Are you looking for a customer or a student?"

		import difflib
		match = lambda sname, name: sname == name or name in sname or difflib.SequenceMatcher(None, sname, name).ratio() >= .75
		exact = [item for item in array if item.name.lower() == name.lower()]
		possibles = [item for item in array if match(item.name.lower(), name.lower())]

		if len(exact) == 1:
			return exact[0]
		elif len(exact) > 1:
			return "There are multiple people that exactly match that query."

		return "Couldn't be found." if len(possibles) == 0 else (possibles[0] if len(possibles) == 1 else [item.name for item in possibles])

	def find_and_act(self, customer_student, name, action):
		array = self.find(customer_student, name)
		if (type(array) == Student) or (type(array) == Customer):
			action(array)
			return s("\n%s", array)
		elif len(array) == 1:
			action(array[0])
			return s("\n%s", array[0])
		else:
			return array

	def show(self, c_s_e, specifier = 'all'):
		if c_s_e == 'e':
			return '\n'.join([s('%s: %s\n', index, expense) for (index, expense) in enumerate(self.expenses)])
		elif specifier == 'all':
			array = self.customers if c_s_e == 'c' else self.gather_students()
			return '\n'.join(s('%s\n', thing) for thing in array)
		else:
			return self.find(c_s_e, specifier)

	def todo(self, c_s, specifier = 'all'):
		if specifier == 'all':
			array = self.customers if c_s == 'c' else self.gather_students()
			return '\n\n'.join(['%s: %s' % (person.name, todo_item) for person in array for todo_item in person.todo()])
		else:
			person = self.find(c_s, specifier)
			if type(person) != Person:
				return person
			return '\n\n'.join('%s' % (todo_item) for todo_item in person.todo())

	def lastweek(self, specifier = 'all'):
		if specifier == 'all':
			array = self.gather_students()
			return '\n\n'.join([s('%s: %s', student.name, student.lessons[-1]) for student in array if student.active and len(student.lessons) > 0])
		else:
			student = self.find('s', specifier)
			return (student.lessons[-1] if len(student.lessons) > 0 else '') if type(student) == Student else student 

	def change(self, c_s_e, name, attr, value, delete = None):
		if c_s_e == 'e':
			if delete == 'd':
				del self.expenses[int(name)]
			elif attr in ['date', 'comments', 'amount']:
				self.expenses[int(name)].change(attr, value)
			else:
				return 'Not a valid attribute.'
			return self.show('e')

		if attr not in {'c':['info', 'name'], 's':['price', 'active', 'birthday', 'name']}[c_s_e]:
			return self.find(c_s_e, name) if c_s_e != 'e' else self.expenses[int(name)]

		if attr == 'birthday':
			import datetime
			value = None if delete == 'd' else datetime.datetime.strptime(value, "%m/%d/%Y")
			function = lambda student: setattr(student, attr, value)
		elif attr == 'info':
			if 'cell' in value.lower():
				# You have to have the carrier value. Somehow
				pass
			function = (lambda customer: customer.contact_info.pop(value)) if delete == 'd' else (lambda customer: customer.contact_info.update(dict_eval(value)))
		elif attr == 'active':
			function = lambda student: setattr(student, attr, mybool(value))
		elif attr in ['price']:
			function = lambda student: setattr(student, attr, float(value))
		else:
			function = (lambda person: delattr(person, attr)) if delete == 'd' else (lambda person: setattr(person, attr, value))
		return self.find_and_act(c_s_e, name, function)

	def deepchange(self, c_s, name, thing, index, attr, value, delete = None):
		if thing not in {'c':['contact', 'payment'], 's':['contact', 'lesson', 'expense']}[c_s]:
			return 'Not a valid thing.'
		
		if delete == 'd':
			action = lambda person: getattr(person,'%ss' % (thing)).pop(int(index))
		else:
			if attr not in {'contact':['from_me', 'resolved'], 'payment':['amount', 'method'], 'lesson':['price'], 'expense':['amount']}[thing] and attr not in ['date', 'comments']:
				return 'Not a valid attribute.'
			action = lambda person: getattr(person,'%ss' % (thing))[int(index)].change(attr, value)
		return self.find_and_act(c_s, name, action)

	def data(self, data_type, specifier = 'all'):
		if data_type in ['financial', 'f']:
			sgive = """Expected Weekly Income: %s """
		elif data_type in ['student', 's']:
			return 0
		elif data_type in ['customer', 'c']:
			return 0

	def add_customer(self, name, contact_info, *students_prices):
		new_students = []
		if len(students_prices) == 1:
			new_students.append(Student(name, float(students_prices[0])))
		else:
			i = 0
			while i < len(students_prices):
				new_students.append(Student(students_prices[i], float(students_prices[i + 1])))
				i += 2

		self.customers.append(Customer(name, contact_info, new_students))
		return self.find('c', name)

	def add_student(self, customer_name, student_name, price):
		customer = self.find('c', customer_name)
		if type(customer) == Customer:
			student = Student(student_name, float(price))
			customer.students.append(student)
			return customer
		else:
			return customer

	def add_expense(self, amount, comments, offset = 0):
		self.expenses.append(Expense(float(amount), comments, offset))
		self.expenses.sort(key = lambda record: record.date)
		return self.show('e', 'all')

	def remind(self, *data):
		if len(data) > 1 and any(is_time(datum) for datum in data):
			names, times = data[::2], data[1::2]

			if (any(is_time(name) for name in names) and any(not is_time(time) for time in times)) or len(names) != len(times):
				return "Your name and time arguments are incorrect."

			name_time = dict(zip(names, times))
			for name, time in name_time.iteritems():
				try:
					addresses = self.get_contact(name)
					for address in addresses:
						message = "Hello this is Blaine Hansen reminding you about your piano lesson tomorrow at %s!" % (time)
						subprocess.call("python messenger.py -a %s -m '%s'" % (address, message), shell=True)
				except BadNameException as e:
					print e.value

		else:
			message = "Hello this is Blaine Hansen reminding you about your piano lesson tomorrow!"
			for name in data:
				try:
					addresses = self.get_contact(name)
					for address in addresses:
						subprocess.call("python messenger.py -a %s -m '%s'" % (address, message), shell=True)
				except BadNameException as e:
					print e.value

	def get_contact(self, name):
		customer = self.find(name)
		if type(customer) == Customer:
			return [value for value in customer.contact_info().values() if '@' in value]
		else:
			raise BadNameException("You have a bad name for %s. Returns: %s" % (name, customer))

	def output(self):
		import os
		dirname = 'studiodata/output/'
		if not os.path.exists(dirname):
			os.mkdir(dirname)
		cd = open(dirname+'contact.ods', 'w'); sd = open(dirname+'student.ods', 'w'); ud = open(dirname+'customer.ods', 'w'); ed = open(dirname+'expense.ods', 'w')
		td = open(dirname+'todo.odt', 'w'); nd = open(dirname+'lastweek.odt', 'w'); bd = open(dirname+'balance.odt', 'w')

		cd.write(contact_prime)
		contact_content = '\n'.join([s('%s\t%s\t%s', customer.name, customer.contact_info, contact.output()) for customer in self.customers for contact in customer.contacts] + [s('%s (%s)\t%s\t%s', student.name, customer.name, customer.contact_info, contact.output()) for customer in self.customers for student in customer.students if student.active for contact in student.contacts])
		cd.write(contact_content)

		sd.write(student_prime)
		student_content = '\n'.join([s('%s\t%s\t%s', customer.name, customer.contact_info, student.output()) for customer in self.customers for student in customer.students if student.active])
		sd.write(student_content)

		sd.write(inactive_student_prime)
		inactive_student_content = '\n'.join([s('%s\t%s\t%s', customer.name, customer.contact_info, student.output()) for customer in self.customers for student in customer.students if not student.active])
		sd.write(inactive_student_content)

		ud.write(customer_prime)
		customer_content = '\n'.join([s('%s', customer.output()) for customer in self.customers])
		ud.write(customer_content)

		ed.write(expense_prime)
		expense_content = '\n'.join([s('%s', expense.output()) for expense in self.expenses])
		ed.write(expense_content)

		td.write("Customers\n\n" + self.todo('c'))
		td.write("\n\nStudents\n\n" + self.todo('s'))

		nd.write(self.lastweek())

		balance_content = '\n\n'.join([s('%s:\n%s', customer.name, customer.balance_statement()) for customer in self.customers if customer.balance() > 0 or any(student.active for student in customer.students)])
		bd.write(balance_content)

		cd.close(); sd.close(); ud.close(); ed.close()
		td.close(); nd.close(); bd.close()
		return 'Output successfully.'

	def gather_students(self):
		return reduce(lambda a, b: a + b, [customer.students for customer in self.customers], [])

class Person(object):

	def __init__(self, name):
		self.name = name
		self.contacts = []

	def make_contact(self, from_me, resolved, comments = "None.", offset = 0):
		self.contacts.append(Contact(mybool(from_me), mybool(resolved), comments, offset))
		self.contacts.sort(key = lambda record: record.date)

	def todo(self):
		return [contact for contact in self.contacts if not contact.resolved]

class Customer(Person):

	def __init__(self, name, contact_info, students):
		super(Customer, self).__init__(name)
		self.payments = []
		self.contact_info = contact_info
		self.students = students

	def customer_make_payment(self, amount, method, comments = "None.", offset = 0):
		self.payments.append(Payment(float(amount), method, comments, offset))
		self.payments.sort(key = lambda record: record.date)

	def owed(self):
		return sum([student.balance() for student in self.students])

	def paid(self):
		return sum([payment.amount for payment in self.payments])
		
	def balance(self):
		return self.owed() - self.paid()

	def balance_statement(self):
		return s("Paid: $%.2f\n", self.paid()) \
			+ 'Payments:\n' + ''.join( [s("%s\n", payment) for payment in self.payments] ) \
			+ ''.join( [s("Total for %s for %s lessons and %s expenses: $%.2f\n", student.name, len(student.lessons), len(student.expenses), student.balance()) for student in self.students] ) \
			+ s("Current balance: $%.2f", self.owed() - self.paid())

	def __str__(self):
		return s("Customer: %s\nBalance: %.2f\n", self.name, self.balance()) \
			+ s('Info: %s\n', self.contact_info) \
			+ 'Payments:\n' + ''.join( [s("%s: %s\n", index, payment) for (index, payment) in enumerate(self.payments)] ) \
			+ 'Contacts:\n' + ''.join( [s("%s: %s\n", index, contact) for (index, contact) in enumerate(self.contacts)] ) \
			+ 'Students:\n' + ''.join( [s("%s: %s\n", student.name, "Active" if student.active else "Not Active") for student in self.students] )

	def output(self):
		return s('%s\t$%.2f\t%s\t\t%s', self.name, self.balance(), self.contact_info, '\t\t'.join([s('%s', payment.output()) for payment in self.payments]))

class Student(Person):

	def __init__(self, name, price):
		# Management stuff.
		super(Student, self).__init__(name)
		self.price = price
		self.lessons = []
		self.expenses = []
		self.active = True

		# Personal stuff.
		self.birthday = None

	def student_add_lesson(self, comments = "None.", offset = 0, price = None):
		price = self.price if price == None else float(price)
		self.lessons.append(Lesson(comments, offset, float(price)))
		self.lessons.sort(key = lambda record: record.date)

	def student_add_expense(self, amount, comments, offset = 0):
		self.expenses.append(Expense(float(amount), comments, offset))
		self.expenses.sort(key = lambda record: record.date)

	def balance(self):
		return sum([lesson.price for lesson in self.lessons]) + sum([expense.amount for expense in self.expenses])

	def __str__(self):
		return s("Student: %s\nPrice: $%.2f\nActive: %s\nBirthday: %s\n", \
			self.name, self.price, self.active, dat(self.birthday)) \
			+ 'Expenses:\n' + ''.join( [s("%s: %s\n", index, expense) for (index, expense) in  enumerate(self.expenses)] ) \
			+ 'Lessons:\n' + ''.join( [s("%s: %s\n", index, lesson) for (index, lesson) in  enumerate(self.lessons)] ) \
			+ 'Contacts:\n' + ''.join( [s("%s: %s\n", index, contact) for (index, contact) in enumerate(self.contacts)] )

	def output(self):
		return s('%s\t$%.2f\t%s', self.name, self.price, '\t\t'.join([s('%s', lesson.output()) for lesson in self.lessons]))

def dict_eval(string):
	# key:value, key:value....
	import re
	p = re.compile('\s*,\s*')
	pairs = filter(None, p.split(string))
	d = {}
	p = re.compile('\s*:\s*')
	for pair in pairs:
		key, value = filter(None, p.split(pair))
		d[cap(key)] = value
	return d


def backup(dirname = 'default'):
	dirname = 'studiodata/backup/%s/' % (dirname)
	# Check if the new directory exists, create if it doesn't.
	import os
	import shutil
	if os.path.exists(dirname):
		shutil.rmtree(dirname)
	os.mkdir(dirname)
	# Copy the files to the new directory.
	shutil.copy(dbfile, dirname)
	return 'Backed up successfully'

dbfile = 'studiodata/studio.db'
dbkey = 'studio'
