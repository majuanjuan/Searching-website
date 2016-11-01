# Searching-website
It's a website with functions as: researching,adding,cutting down.

As deployment I use Apache httpd and mod_wsgi.

Step:
1.setup mod_wsgi with :#yum install mod_wsgi.

2.edit conf doocument with : # vi /etc/httpd/conf/httpd.conf
insert these into httpd.conf:
< VirtualHost *>
 ServerName example.com

 WSGIScriptAlias / /var/www/app/service.wsgi
 WSGIScriptReloading On

 < Directory /var/www/html/appname/>
     Order deny,allow
     Allow from all
 < /Directory>
< /VirtualHost>

3.move your app into /var/www/html

4.edit service.wsgi and insert:
import sys
sys.path.insert(0, '/var/www/html/appname/')
from appname import app as application

5.If any error ,please checkout error_log at /var/log/httpd/error_log

6.Open your terminal and run : service httpd start
and then http://your-own-ip will give you a glad welcome.
