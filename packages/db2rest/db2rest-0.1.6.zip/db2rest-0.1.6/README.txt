Databased to REST API
=====================

![image](https://pypip.in/v/db2rest/badge.png) ![image](https://pypip.in/d/db2rest/badge.png)
![image](https://travis-ci.org/nikpalumbo/db2rest.png?branch=master)

db2rest provides a HTTP REST API for relational databases. You might
find it most useful for tasks where you want access the database by
using the HTTP protocol.

Installation
------------

Egg and source files for this project are hosted on PyPi. You should be able to use
pip to automatically install this project.

    pip install db2rest

Configuration
-------------

    edit YOUR_PACKAGE_PATH:db2rest/confing.example

In order to connect to the database modify the string connection and the
configure LDAP to provied to the API a way to authorize the users.

    [db]
    string_connection: mysql://USER:@127.0.0.1:PORT/dbname

    [webserver]
    host: 127.0.0.1
    port: 5000

    [logger]
    level: DEBUG

    [ldap]
    active: false
    string_connection: ldap://LDAPSERVER
    query:              MYQUERY

Rename it:

    YOUR_PACKAGE_PATH:db2rest/config.cfg

Example
-------

Type the following command:

    db2rest-run

or,

    db2rest-run YOUR_CONFIG_FILE 

If everthing went fine you should be able to see the following two
lines:

    INFO:werkzeug: * Running on http://127.0.0.1:5000/
    INFO:werkzeug: * Restarting with reloader

To query your database from command line using curl
---------------------------------------------------

Set you password in this way the password isn't in the history's shell:

    read -s -p "Enter Password: " mypassword
    Enter Password:********

* * * * *

To get all tables present in the databases:

    curl --user usernmae:$mypassword -i -H "Accept: application/json" -X GET  http://localhost:5000/  

* * * * *

To get all row from a table in the database:

    curl --user usernmae:$mypassword -i -H "Accept: application/json" -X GET  http://localhost:5000/mytablename 

* * * * *

To update a field of a row:

    curl --user usernmae:$mypassword -i -H "Accept: application/json" -X PUT  -d "myfield=myvalue "http://localhost:5000/mytablename/myid 


GIT and Continuos Integration
-----------------------------

I like Bitbucket so I published the packages at:

> <https://bitbucket.org/nikpalumbo/db2rest>

In order to use the continuos service integration and multiple enviroment runtimes provided by Travis-Ci this packages is also on GitHub at the following address.

> <https://github.com/nikpalumbo/db2rest.git>

To keep the two repositories syncronized add the urls to your .git/config as following:
	
	…
	[remote "origin"]
		url = https://nikpalumbo@bitbucket.org/nikpalumbo/db2rest.git
	    url = https://github.com/nikpalumbo/db2rest.git
        fetch = +refs/heads/*:refs/remotes/origin/*
	…

Release the package
-------------------
To either register the package (only once), or update the package's metadata execute the following command in root dir of the package:
	
	python setup.py register  


To realease this package in two format .gz and .zip use the following command is used to realease a new version:
	
	python setup.py sdist --formats=gztar,zip  upload

if you want to make avaible the packages also as egg-files:
	 
	python setup.py bdist_egg upload

The packages is available at:

> <https://pypi.python.org/pypi/db2rest>


Apache and CGI Config
---------------------
	<VirtualHost *:80>
    	ServerAdmin myemail@server.com
    	ServerName myservername
    	ServerAlias myalias1 myalias2
   
    	DocumentRoot /srv/mydocumenteroot/
    <Directory /srv/mydocumenteroot/>
	    Options Indexes FollowSymLinks MultiViews +ExecCGI
            AllowOverride None
            Order allow,deny
            allow from all
	    AddHandler cgi-script .cgi
	    AuthType Basic
           
        Require valid-user
    </Directory>
     
    RewriteEngine On
    RewriteRule ^/(.*)$ /srv/mydocumenteroot/db2rest.cgi/$1 [QSA,L]
    ErrorLog ${APACHE_LOG_DIR}/myaccess-api_error.log
    CustomLog ${APACHE_LOG_DIR}/myaerror-api_access.log combined

	</VirtualHost>
