CROWDFEED
---------
This is a utility web application used for various projects to solve usually quick and small problems where a web server is required.

It was initially created to act as a proxy to grab data from the yellowpages api so that I can cache results in memory and not have to worry about going over api limit.

Here is an example : 
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
     
It is also being used by the mwc, christmas party and video concierge demos.

Requirements :
    * python
    * twisted 

Using :
    ~:python get_crowdfeed.py
    ~:python get_upload.py
