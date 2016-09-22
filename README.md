                                Django Bookmark Application

This is an application created using Python and Django Web Framework based on Learning Website Development With Django by Ayman Hourieh. The project is a complex system and some of the features that i have implemented on this project include:

    - Main page where a display of welcome message to the user is shown and a list of shared bookmrks
    - There is site navigation to assist the user in using the app. You can sign up, login and bookmarks and choose whether to share or not. You can also add friends and invite friends.
    - For my backend I decided to user mysql.
    - In the project i have also implement a simple caching system for the whole site. You can test this by running the following commands:
    
               1. python manage.py shell
               2. from django.test.client import Client
               3. client = Client()
               4. response = client.get('/')
               5. print response

    - If you decided you want to test whethe your can send invitation, you have to putting you setting of the Internet Service provider in the setting.py
    - Some of the cool features about this project can be implement on other project
    
The project is fun to implement, Django is fun. Download the project and play around with it.