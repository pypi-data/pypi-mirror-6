PushCo -a Python API for push.co 


Pushco is a simple API to provide access to your push.co app.
Register one at http://push.co, you will get an API key and an API secret assigned


Install::
	
	pip install pushco 


Typical usage would be::



    from pushco import Pushco

    API_KEY = 'your API key'
    API_SECRET ='your API secret'
	
    p = Pushco(API_KEY, API_SECRET, 'Hi, this is a push message')
    p.push()

    #url view
    p = Pushco(API_KEY, API_SECRET, 'Click for Python', url = 'http://python.org')
    p.push()
	
    #map view
    p = Pushco(API_KEY, API_SECRET,'London', latitude = '51.5072', longitude='0.1275')
    p.push()