#!/usr/bin/python

import smtplib
import sys
import getopt

def main(argv):
	print argv
	getopt.getopt(argv,"a:m:",["address=", "message="])
	try:
		opts, args = getopt.getopt(argv,"a:m:",["address=", "message="])
	except getopt.GetoptError:
		print 'messenger.py -a address -m message'
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-a", "--address"):
			address = arg
		elif opt in ("-m", "--message"):
			message = arg
	print 'Address and Message are: %s, %s.' % (address, message)
	if address is None or message is None:
		print 'Both arguments must be defined.'
		sys.exit(2)

	fromaddress = 'dummy@gmail.com'

	# Credentials (if needed)
	username = 'dummy'
	password = 'secretpassword'

	# The actual mail send
	server = smtplib.SMTP('smtp.gmail.com:587')
	server.starttls()
	server.login(username,password)
	server.sendmail(fromaddress, address, message)
	server.quit()

if __name__ == "__main__":
   main(sys.argv[1:])