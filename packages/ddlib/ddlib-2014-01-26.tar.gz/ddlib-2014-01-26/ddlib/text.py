#-*- coding: utf-8 -*-

import re
import sys
import random
import datetime




POLSKIE_ZNAKI_MAP = {
	'ę':'e',
	'ó':'o',
	'ą':'a',
	'ś':'s',
	'ł':'l',
	'ż':'z',
	'ź':'z',
	'ć':'c',
	'ń':'n',

	'Ę':'E',
	'Ó':'O',
	'Ą':'A',
	'Ś':'S',
	'Ł':'L',
	'Ż':'Z',
	'Ź':'Z',
	'Ć':'C',
	'Ń':'N',
}





def log(s, level='', name=''):
	if name:
		level = ('%s\t%s' % (level, name)).strip()

	level = '\t%s'%level if level else ''

	print('%s%s\t%s' % (datetime.datetime.now(), level, s))
	sys.stdout.flush()


def log_debug(s):
	log(s, 'DEBUG')


def log_info(s):
	log(s, 'INFO')


def log_error(s):
	log(s, 'ERROR')






def gets(txt, begin, end=None):
	"""
		Gets some text between <begin> and <end> of <txt>.

		eg:
		>>> out = gets('This is sample text.', ' is ', ' text.')
		>>> print(out)
		'sample'

	"""
	out = None
	b = txt.find(begin)
	if b != -1:
		out = txt[b+len(begin):]
		if end:
			e = out.find(end)
			if e != -1:
				out = out[:e]

	return out





def random_string(dlugosc=10, dozwolone_znaki='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'):
	"""
		Generator losowych ciągłów znaków o wyznaczonej długości.
		Może zostać wykorzystany jako np: generator haseł.

		Arguments:
			dlugosc -- <int> długość wynikowego ciągu znaków
			dozwolone_znaki -- <str> ciąg znaków jakie zostaną użyte

		Return:
			<str> losowy ciag znaków o długości `dlugosc` stworzony ze znaków `dozwolone_znaki`

		Example:
			a = random_string(12)
			print(a)
	"""
	return ''.join(random.choice(dozwolone_znaki) for x in range(dlugosc))





def rm_polish_chars(s):
	"""
		Zastępuje polskie znaki odpowiednikami bez ogonków.

		Arguments:
			s -- <str> wyrarzenie z jakiego zostanie wygenerowany wynik

		Return:
			<str> ciąg znaków pozbawiony polskich znaków.

		Example:
			a = rm_polish_chars('To jest mój nowy fajny tytuł :] !!')
			print(a)
			'To jest moj nowy fajny tytul :] !!'
	"""
	for k,v in POLSKIE_ZNAKI_MAP.items():
		s = s.replace(k,v)

	return s




def nice_key(s):
	"""
		Generator przyjemnych ciągów znaków.
		Może zostać wykorzystany do tworzenia adresów URL lub ID w bazie danych.
		Zwracane ciągni nie zawierają spacji, ani też żadnych dziwnych znaów.

		Arguments:
			s -- <str> wyrarzenie z jakiego zostanie wygenerowany wynik

		Return:
			<str> ciąg znaków nie zawierający spacji, ani też żadnych dziwnych znaów. Wyłącznie ASCII.

		Example:
			a = nice_key('To jest mój nowy fajny tytuł :] !!')
			print(a)
			'to-jest-moj-nowy-fajny-tytul'
	"""
	s = rm_polish_chars(s.lower())
	s = re.sub('[^0-9a-z]','-',s).strip('-')
	s = re.sub('[-]+','-',s)
	return s
