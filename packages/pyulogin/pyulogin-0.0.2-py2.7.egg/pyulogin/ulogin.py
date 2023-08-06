'''
Copyright (c)2014 Gurov Dmitri 

See the file license.txt for copying permission.

this file contains constans and data necessary for work with ulogin service:

url-- URL of ulogin's data provider(handler of this URL transform token to actual user data) 

fields-- list of all available field of user's profile from ulogin

UloginError -- dictionary with exceptions 
 '''

import exceptions
url = 'http://ulogin.ru/token.php'
fields = ['first_name','last_name','email','nickname','bdate','sex',
'phone','photo','photo_big','city','country','network','profile','uid','identity','manual','verified_email']
UloginError={'token expired':exceptions.TokenExpired,'invalid token':exceptions.InvalidToken,'host is not XXX':exceptions.HostError}
