'''
Copyright (c)2014 Gurov Dmitri 

See the file license.txt for copying permission.

UloginUser -- basic class with information about user. Class'es field were created dynamicly from    
fields parametr of constructor. 

 
fields -- dictionary with necessary for developer fields.  class field id obtain vlue from field 'uid'     
'''


class UloginUser:
	def __init__(self,fields):
		for field in fields.keys():
			setattr(self,field,fields[field])
		self.id = fields['uid']	
	 

			
		

