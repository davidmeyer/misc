#! /usr/local/bin/python

#
#	canonicalize_c1.py --
#
#	Canonicalize and sum up the "descriptions". The fields of
#	interest here in the rows of the csv from capitalone.com 
#	are:
#
#		row[3]: the description, used as a key here
#		row[5]: the amount debited (None if credit)
#		row[6]: the amount credited (not used here)
#
#	The format of the csv output at the end (df.to_csv) is
#	designed for excel tables of various types.   
#	
#	David Meyer
#	dmm@1-4-5.net
#	Fri Aug 10 14:36:01 PDT 2018
#	$Header: $

import sys
import csv
import re
import argparse
import pandas as pd

#
#	There are weird patters in the description fields. this
#	function tries to remove them. Square has at least 4 different
#	patterns AFICT. Better would be a CFG describing what the 
#	Descriptions look like.
#

def canonicalize_item(item):
	item = item.lower().rstrip()
	item = re.sub(r'[#0-9]*',                    r'',            item)
	item = re.sub(r'sq[a-z\t\s\*]*sq[\t\s\*]*' , r'',            item)
	item = re.sub(r'target*',                    r'target',      item) 
	item = re.sub(r'subway*',                    r'subway',      item) 
	item = re.sub(r'wholefds[a-z\s\t]+',         r'wholefoods',  item) 
	item = re.sub(r'starbucks[#a-z0-9\s\t]*',    r'starbucks',   item) 
	item = re.sub(r'trader joe\'s[a-z\s\t]+',    r'trader joes', item) 
	return(item)

#
#	main(argv) --
#

def main(argv):

#
#	Be lazy, get control globals
#

	DEBUG			= 0

#
#	Use these data structures to canonicalize CapitalOne's description 
#	field (in their exported csvs), and keep a running total for
#	canonicalized_description in canonicalizedDict.get(...))
#

	canonicalized_description = ""
	canonicalizedDict         = {}		# canonicalized names and sums
	sum                       = float(0)	# running sum

#
#	Simple a (really simple) arg parser
#

	parser = argparse.ArgumentParser()

#
#	Add a file argument. -o or --ofile. Default
#	to sys.stdout.
#
#	Note: -h and --help are there by default
#

	parser.add_argument("-o",
			    "--ofile",
			    action  = "store",
			    dest    = "ofile",
	                    help    = "output file (default: sys.stdout)",
			    default = sys.stdout)


	parser.add_argument("-i",
			    "--ifile",
			    action  = "store",
			    dest    = "ifile",
	                    help    = "input file (default: sys.stdin)",
			    default = sys.stdin)


	results = parser.parse_args()
	ofile   = results.ofile			# default to sys.stdout
        ifile   = results.ifile

#
#	ifile could be sys.stdin, which is an open file
#	if could also be a string, so we have to open the
#	corresponding file
#
	if (ifile != sys.stdin):
		try: 
			ifile = open(ifile, "r")
		except IOError:
			print "Can't open", ifile
			return



#	Now fire up the csv reader
#

        reader = csv.reader(ifile, delimiter=',', quotechar='"')

#
#	For any row that is a credit row[5] = None (the credit amount
#	in in row[6]). Check for that so that we don't blow up trying 
#	to execute float(None)
#

        for row in reader:
		try:
		    sum = float(row[5])
		except ValueError:	      # discard this row (its a credit)
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

	df.to_csv(ofile, float_format='%.2f', header = False)

#
#	
#

if __name__ == "__main__":
        main(sys.argv)
