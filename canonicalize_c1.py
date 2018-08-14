#! /usr/local/bin/python

#
#	Canonicalize and sum up the descriptions from different
#	vendors that you get if you export a csv from Capitalone. 
#	The source .csv is from https://www.capitalone.com. Format of
#	the csv output at the end (print_csv) is designed for excel 
#	tables of various types. 
#
#	dmm@1-4-5.net
#	Sun Aug 12 14:36:01 PDT 2018
#	$Header: $
#

import csv
import os
import sys
import time
import io
import datetime 
import re
import getpass
import pwd
import argparse
import pandas as pd
import matplotlib.pyplot as plt

#
#	There are weird patters in the description fields. this
#	function tries to remove them. Square has at least 4 different
#	patterns AFICT.
#

def canonicalize_item(item):
	item = item.lower().rstrip()
	item = re.sub(r'[#0-9]*',                    r'', item)
	item = re.sub(r'sq[a-z\t\s\*]*sq[\t\s\*]*' , r'', item)
	item = re.sub(r'target*',                    r'target', item) 
	item = re.sub(r'subway*',                    r'subway', item) 
	item = re.sub(r'wholefds*',                  r'wholefoods', item) 
	item = re.sub(r'starbucks[#a-z0-9\s\t]*',    r'starbucks', item) 
	item = re.sub(r'trader joe\'s[a-z\s\t]+',    r'trader joes', item) 
	return(item)

#
#	print_csv(Dict) --
#
#	Print Dict as a key,value csv. Sort in reverse order.
#

def print_csv(Dict):
	for key, value in sorted(Dict.iteritems(),
				 key     = lambda (k,v): (v,k),
				 reverse = True):
		print "%s,%.2f" % (key, value)

#
#	print_df_as_csv(df) --
#
#	Lots of ways to do this. This seems easist.
#
#
def print_df_as_csv(df):
	for index, row in df.iterrows():
	   print "{0},{1}".format(index, float(row[0]))


#
#	date and comment stuff
#
def format_comment():
	now               = datetime.datetime.now()
	date_string       = now.strftime('%Y-%m-%d')
	who               = pwd.getpwuid(os.getuid())[4]
	email             = "{}@1-4-5.net".format(getpass.getuser())
	comment_string    = \
	"#\n#\tCapitalOne Savor csv\n#\n#\n#\n#\t{}\n#\t{}\n#\t{}\n#\n"
	return(comment_string.format(who,email,date_string))
#
#
#	write a comment at the front of the file
#
#	don't know if this works with excel (what is the 
#	excel comment character).
#
#
def csv_comment(file):
	try:
		f = open(file, 'r+')
		file_data = f.read()
		f.seek(0, 0)
		f.write(format_comment().rstrip('\r\n') + '\n' + file_data)
	except IOError as e:
		print "I/O error({0}): {1}".format(e.errno, e.strerror)
	except ValueError:
		print "Could not convert data to an integer."
	except:
		print "Unexpected error:", sys.exc_info()[0]
		raise
#
#	main(argv) --
#
#

def main(argv):

#
#	Be lazy, get control globals
#
	DEBUG			= 0
	ADD_COMMENT		= 0

#
#	Use these data structures to canonicalize CapitalOne's description 
#	field (in their exported csvs), and keep a running total for
#	canonicalized_description in 
#	canonicalizedDict.get(canonicalized_description))
#

	canonicalized_description = ""
	canonicalizedDict         = {}		# canonicalized names and sums
	sum                       = float(0)	# running sum

#
#	Simple a (really simple) arg parser
#

	parser = argparse.ArgumentParser()

#
#	Add a file argument. -f or --file. Default
#	to sys.stdout.
#
#	Note: -h and --help are there by default
#

	parser.add_argument("-f",
			    "--file",
			    action = "store",
			    dest   = "file",
	                    help   = "output file (default: sys.stdout)",
			    default=sys.stdout)
	results    = parser.parse_args()
	output_csv = results.file		# default to sys.stdout

#
#	Now fire up the csv reader
#

        reader = csv.reader(sys.stdin, delimiter=',', quotechar='"')

#
#	For any row that is a credit row[5] = None (the credit amount
#	in in row[6]). Check for that so that we don't blow up trying 
#	to execute float(None)
#

        for row in reader:
		try:
		    sum = float(row[5])
		except ValueError:		# discard this row
	            continue

#
#	If canonicalizedDict.get(canonicalized_description) == None then
#	then set the value to the current sum (sum = float(row[5])). 
#	Otherwise canonicalizedDict.get(canonicalized_description) is 
#	the running sum for canonicalized_description. In this case add 
#	the the current value for canonicalized_description to the 
#	current sum (which again is float(row[5])). 
#

                canonicalized_description = canonicalize_item(row[3]).strip()
                if  (canonicalizedDict.get(canonicalized_description)): 
                        sum += canonicalizedDict.get(canonicalized_description)
                canonicalizedDict.update({canonicalized_description : sum})

#
#	Now build a sorted pandas dataframe from canonicalizedDict 
#

	df = pd.DataFrame.from_dict(canonicalizedDict,
				    columns = ['Sum'],
				    orient  = 'index') \
				    .sort_values('Sum', ascending = False)


#
#	convert dataframe to csv for use with excel
#

	df.to_csv(output_csv, float_format='%.2f', header = False)

	if (ADD_COMMENT): 
		csv_comment(output_csv)
#
#
#
if __name__ == "__main__":
        main(sys.argv)
