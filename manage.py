from management import *
import readline
import os
import shelve

def wrap_up():
	print studio.output()
	db = shelve.open(dbfile)
	db[dbkey] = studio
	db.close()

import signal
import sys
def signal_handler(signal, frame):
	print 'You pressed Ctrl+C!'
	wrap_up()
	sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

wish = """
data; financial|student|customer;
"""

help_string = """
show; customer|student|expense; <name>;

change; customer|student|expense; name; attr; value; <delete>;

deepchange; customer|student; name; type; index; attr; value; <delete>;

customer; name; type:info,... ; student_name; student_price;...

student; customer_name; student_name; student_price;

lesson; name; comments; <offset>; <price>;

studentexpense; name; amount; comments; <offset>; 

contact; customer|student; name; from_me; resolved; comments; <offset>;

payment; name; amount; method; comments; <offset>;

expense; amount; comments; <offset>;

remind; name; <time>; ...

backup; <dirname>;

lastweek; <specifier>;

todo; customer|student; <specifier>;
"""

db = shelve.open(dbfile)
studio = db[dbkey]
db.close()

backup()

basic_prompt = 'Enter a command. Type "help" for help.\n'
i = raw_input(basic_prompt);
while(i != 'exit' and i != 'done'):
	
	try:

		import re
		p = re.compile('\s*;\s*')
		tokens = [t for t in p.split(i) if t]
		command, args = tokens[0], tokens[1:]

		# Help
		if command == 'help':
			print help_string

		# Show an item, or all items
		elif command == 'show':
			print studio.show(*tuple(args))

		# Change an attribute.
		elif command == 'change':
			print studio.change(*tuple(args))

		# When we need to change the internals of records.
		elif command == 'deepchange':
			print studio.deepchange(*tuple(args))

		# New customer
		elif command == 'customer':
			print studio.add_customer(args[0], dict_eval(args[1]), *tuple(args[2:]))

		# New student
		elif command == 'student':
			print studio.add_student(args[0], args[1], args[2])

		# Lesson done
		elif command == 'lesson':
			action = lambda student: student.student_add_lesson(*tuple(args[1:]))
			print studio.find_and_act('s', args[0], action)

		elif command == 'studentexpense':
			action = lambda student: student.student_add_expense(*tuple(args[1:]))
			print studio.find_and_act('s', args[0], action)

		# Contact made
		elif command == 'contact':
			action = lambda person: person.make_contact(*tuple(args[2:]))
			print studio.find_and_act(args[0], args[1], action)

		# Payment made
		elif command == 'payment':
			action = lambda customer: customer.customer_make_payment(*tuple(args[1:]))
			print studio.find_and_act('c', args[0], action)

		# Expense incurred.
		elif command == 'expense':
			print studio.add_expense(*tuple(args))

		elif command == 'remind':
			print studio.remind(*tuple(args))

		# Back up the studio data.
		elif command == 'backup':
			print backup(*tuple(args))

		# Get a list of the things that are unresolved.
		elif command == 'todo':
			print studio.todo(*tuple(args))

		# Print out last week's lesson.
		elif command == 'lastweek':
			print studio.lastweek(*tuple(args))

		# Show valuable indicators.
		elif command == 'data':
			print studio.data(*tuple(args))

	except Exception, e:
		print e
		i = raw_input(basic_prompt)
	else:
		i = raw_input(basic_prompt)
	
wrap_up()
raw_input()