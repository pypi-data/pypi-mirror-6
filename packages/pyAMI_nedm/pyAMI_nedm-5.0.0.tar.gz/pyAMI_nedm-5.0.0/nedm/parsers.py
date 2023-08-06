#############################################################################
# Author  : Jerome ODIER
#
# Email   : jerome.odier@cern.ch
#           jerome.odier@lpsc.in2p3.fr
#
# Version : 1.X.X for nEMD (2013-2014)
#
#############################################################################

import re, gzip, nedm.exception, pyAMI.my_tokenizer

#############################################################################

def gz_read(file_name, is_binary = False):

	try:
		if is_binary == False:
			f = gzip.open(file_name, 'rt')
		else:
			f = gzip.open(file_name, 'rb')

		result = f.read()

		f.close()

	except IOError:
		raise nedm.exception.NEDMException('error: could not open `%s`' % file_name)

	return result

#############################################################################

def parse_dict(file_name, first_key):
	data = gz_read(file_name)

	lines = data.split('\n')

	result = []

	try:

		for line in lines:
			vals, lines = pyAMI.my_tokenizer.tokenize(
				line,
				spaces = [' ', '\t', '\r'],
				symbols = ['#'],
				strings = [['\'', '\''], ['\"', '\"']]
			)

			if len(vals) > 0:

				if vals[0].startswith('#'):
					#####################################
					# READ KEYS                         #
					#####################################

					if len(vals) > 1 and vals[1] == first_key:
						keys = vals[1: ]

					#####################################

				else:
					#####################################
					# READ DATA                         #
					#####################################

					if len(vals) == len(keys):
					
						if len(vals[0]) > 0:
							result.append(dict(zip(keys, vals)))

					else:
						raise nedm.exception.NEDMException('error: invalid file `%s`' % file_name)

					#####################################

	except nedm.exception.NEDMException:
		raise nedm.exception.NEDMException('error: invalid file `%s`' % file_name)

	return result

#############################################################################

def parse_list(file_name, min):
	data = gz_read(file_name)

	lines = data.split('\n')

	result = []

	try:

		for line in lines:
			vals, lines = pyAMI.my_tokenizer.tokenize(
				line,
				spaces = [' ', '\t', '\r'],
				symbols = ['#'],
				strings = [['\'', '\''], ['\"', '\"']]
			)

			if len(vals) > min and not vals[0].startswith('#'):
				result.append(vals)

	except nedm.exception.NEDMException:
		raise nedm.exception.NEDMException('error: invalid file `%s`' % file_name)

	return result

#############################################################################

def parse_meta_file(file_name):
	return parse_dict(file_name, '______Date_and_Time______')

#############################################################################

def parse_slow_control_file(file_name):
	return parse_list(file_name, 1)

#############################################################################
