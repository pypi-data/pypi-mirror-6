'''
Copyright (c)2014 Gurov Dmitri 

See the file license.txt for copying permission.

exceptios.py  is  module for various exceptions. Three exception classes were defined in module:
1. InvalidToken -- this exception raised when service return json answer with error message:  invalid token
2. TokenExpired -- this exception raised when service return json answer with error message:  token expired
3. HostError --    this exception raised when service return json answer with error message:  host is not XXX
see http://ulogin.ru/help.php#faq

Every excepton class has two field:
socnet - name of social network 
value - error message 
''' 


class InvalidToken(Exception):
	def __init__(self,value,socnet):
		self.socnet = socnet 
		self.value = value 

	def __str__(self):
		return  repr ('During  authorizing process through service '+ self.socnet+' error occured:' + self.value)

class TokenExpired(Exception):
	def __init__(self,value,socnet):
		self.socnet = socnet 
		self.value = value 

	def __str__(self):
		return  repr ('During  authorizing process through service '+ self.socnet+' error occured:' + self.value)

class HostError(Exception):
	def __init__(self,value,socnet):
		self.socnet = socnet 
		self.value = value 

	def __str__(self):
		return  repr ('During  authorizing process through service '+ self.socnet+' error occured:' + self.value)
