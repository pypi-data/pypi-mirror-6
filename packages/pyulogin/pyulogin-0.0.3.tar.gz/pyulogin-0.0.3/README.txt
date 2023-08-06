==Overwiew of package==
This package is wrapper for uLogin(ulogin.ru) service. service uLogin is oAuth provider,wich can work with many different social network: facebook,google,twitter and other. Service can get you JSON answer with information about user. This package can execute query to uLogin service and parse information about user. Wrapper can return to your programm class with fields from uLogin answer.  
==Usage ==
First,install uLogin panel on your site from http://ulogin.ru/constructor.php
Second,uLogin send token of user on some URL of your site. You can add any URL of your site  in settings of panel for this task. Write handler for this URL. Now,you can use this wrapper:

           
