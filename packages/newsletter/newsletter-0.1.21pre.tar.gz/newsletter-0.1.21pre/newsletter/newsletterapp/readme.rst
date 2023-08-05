newsletterapp
=============

A demonstration application for the newsletter library.

People subscribe to the newsletter, and then you send them newsletters.

If they get sick of them they can unsubscribe.

Features:
---------

* sends html email to hundreds of subscribers
* html editor
* No database setup. uses sqlite files instead of a database.
* html templates are customisable. For emails, front end and admin areas.
* web interface, and command line interface.  Admin area password protected.
* unsubscribes handled.
* a modern python code base, with tests and documentation.
* import from csv files.
* send throttling, so you can reduce the impact on your email server.
* external or local email server.
* configuration of many options through a .ini configuration file.
* dynamic, per user variables like %fullname% in emails.


Limitations:
------------

* sqlite concurrent access is not as great as a database like postgresql
* no automatic bounce processing.  You'll have to do this manually.
* does not attempt to track opens.
* no through the web configuration of all attributes.
* ... plenty of other limitations.





Description of files and directories
------------------------------------

* newsletterapp.py is the main script.
* newsletterapp.ini
* test_newsletterapp.py is a test for the app.
* log is where log files are stored.
* db is the directory where the database files are stored.
* static is where html templates, css, js are stored.


db
~~

Contains a directory of files.

* newsletter_sends.sqlitepickle
* subscribers.sqlitepickle
* send_parts.sqlitepickle



static
~~~~~~
Directory of static files used in the app.  

Templates for front end pages, admin pages and email templates.

* css
* js
* web_front_templates
* email_templates
* tiny_mce
* images
* web_admin_templates






