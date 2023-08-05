import re

class ValidationModel(object):

	def __init__(self, value):
		""" przypisujemy nasza wartosc """
		self.value = value


	def len(self, min, max=None):
		""" sprawdzamy czy dlugosc naszej wartosci jest w miedzy `min` a `max` """
		if max is None:
			return min <= len(self.value or '')
		else:
			return min <= len(self.value or '') <= max


	def in_set(self, *values):
		""" sprawdzamy czy nasza wartosc jest w zbiorze """
		return self.value in set(values)


	def login(self):
		""" w loginie dopuszczalne znaki a-z 0-9 _ - oraz musi zaczynac sie od litery """
		s = self.value
		if not s: return False
		if not 'a' <= s[0] <= 'z': return False
		return len(re.sub('[a-z0-9\-]','',s)) == 0


	def password(self, min, max=None):
		""" sprawdzamy moc hasla i czy jest poprawne """
		if self.len(min, max) and self.value.isalnum():
			strength = 0
			if self.value.lower() != self.value: strength += 1
			if len([x for x in self.value if x.isdigit()]) > 0: strength += 1
			if len([x for x in self.value if not x.isalnum()]) > 0: strength += 1
			return strength > 2

		return False


	def email(self):
		""" sprawdzamy czy nasza wartosc jest poprawnym e-mailem """
		assert isinstance(self.value, str), "self.value musi byc <str>"
		if len(self.value) > 4:
			if re.match('^[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$', self.value.lower()) != None:
				return True

		return False


	def url(self):
		""" sprawdzamy czy nasza wartosc jest poprawnym URLem """
		# TODO:
		if len(self.value) > 2:
			return True

		return False


	def domain(self):
		""" sprawdzamy czy nasza wartosc jest poprawną domeną """
		# TODO: wywalic http:// i wszystko po /index.html
		# tj. wyciagnac sama domene
		if len(self.value) > 2:
			return True

		return False


	def phone(self):
		""" sprawdzamy czy to polski telefon lub fax """
		return re.match('^[1-9][0-9]{8}([#][0-9]{1,4})?$', self.value) is not None


	def zipcode(self):
		""" sprawdzamy czy to poprawny kod pocztowy """
		from .region import get_ids
		if len(self.value) != 6: return False
		return False if get_ids(self.value) is None else True


	def alphanumeric(self):
		""" sprawdzamy czy nasza wartosc jest alphanumericsumary (literki lub cyferki) """
		return self.value.isalnum()


	def alphalower(self):
		""" sprawdzamy czy nasza wartosc jest alphalower (wylacznie male literki) """
		return self.value.isalpha() and self.value.lower() == self.value


	def nip(self):
		if self.value is None: return True
		nip = self.value.replace('-', '')
		suma = 0
		if nip.isdigit() and len(nip) == 10:
			for i in enumerate(nip[:-1]):
				suma += ( int(i[1]) * [6, 5, 7, 2, 3, 4, 5, 6, 7][i[0]] )
			div1 = divmod(suma, 11)
			div2 = divmod(div1[1], 10)
			if int(nip[-1]) == div2[1]:
				return True

		return False


	def regon(self):
		regon = re.sub('[^0-9]','',self.value)
		weights = { 7: (2, 3, 4, 5, 6, 7), 9: (8, 9, 2, 3, 4, 5, 6, 7), 14: (2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8), }
		try:
			regon = map(int, regon)
			weights = weights[len(regon)]
		except:
			return False

		checksum = sum(n * w for n, w in zip(regon, weights))
		return checksum % 11 % 10 == regon[-1]













def is_email(v): return ValidationModel(v).email()
def is_phone(v): return ValidationModel(v).phone()
def is_zipcode(v): return ValidationModel(v).zipcode()

