CROWDFEED
---------
This is going to be really cool but for now I'm just using it as a proxy to grab data from yellowpages api so that I can cache results in memory and not have to worry about going over api limit.

Its going to be very basic.

Do get request ie /
    http://crowdfeed.conversationboard.com?q=pizza

Returns ten results in json format ie/
    [ 
        {'name':'Pizza Pizza',
         'phone_number' : '416.441.3594',
         'location' : 'Don Mills and Eglinton',
         'image_url' : 'http://jeevers.jpg'
        }
    ] 
     
        
