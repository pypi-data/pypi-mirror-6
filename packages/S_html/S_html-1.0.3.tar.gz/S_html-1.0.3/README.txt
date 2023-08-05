===========
   S-HTML
===========

S-HTML is a simple and easy to use HTML OOP Web Framework to use with WSGI

==================================
1.- Install Mod_WSGI for Python 3:
==================================
in Debian like systems type:
	apt-get install libapache2-mod-wsgi-py3

==============================
2.- Configure the virtual host
==============================
Changes to the DEFAULT file
The file /etc/apache2/sites-available/default needs to be modified:

	DocumentRoot /var/www/public_name
	WSGIScriptAlias /public_name /var/www/path_to_application/application.wsgi

Your folder structure should look like the following scheme:
	/var/www/
	├── path_to_application/
	│	├── application.wsgi
	│	└── python_modules/
	└── public_name/
		├── css/
		├── js/
		├── images/
		└── other_fix_content/

Restart the Apache server:
	service apache2 restart

====================================
3.- Create the application.wsgi file
====================================
Use the following demo to test the S-HTML capabilities:

# -*- coding: utf-8 *-*
import os, sys, Pi_html

def application(environ, start_response):
  request = environ['REQUEST_URI']
  if not request.find("?") == -1:
    (url_path, query_string) = request.split("?")
  else:
    url_path = request
    query_string = ""  
  if url_path == "/path_to_application/debug":
    if environ['REQUEST_METHOD'] == 'GET':
      get = S_html.fetchQueryString(query_string.split("&"))
      result = "GET : <br />Array<br />{<br />"
      for key in get.keys():
        result += "&nbsp;" * 4 + "[{}]".format(key) + " => " + get[key] + "<br />"
      result += "}"
    if environ['REQUEST_METHOD'] == 'POST':
      post = S_html.fetchPost(environ['wsgi.input'])
      result = "POST : <br />Array<br />{<br />"
      for key in post.keys():
        result += "&nbsp;" * 4 + "[{}]".format(key) + " => " + post[key] + "<br />"
      result += "}"
  elif url_path == "/pi_html":
    page = S_html.Pi_html("Pi_HTML Class Demo")
    page.add_pageTabs([["Index", "index", True],
		   ["Edit", "edit", False],
		   ["New", "new", False]])
    page.add_bodyContent(page.tag("h2", "", request))

    frmDemo = S_html.Form("frmDemo", "/path_to_application/debug", "post", "Submit")
    frmDemo.add_item("Text", "text", "Some Value", "text", "required")
    frmDemo.add_item("Password", "password", "Some Value", "password", "")
    frmDemo.add_item("Date", "date", "2013-12-12", "date", "")
    frmDemo.add_item("Number", "number", "80", "number", "min='0' max='100'step='1'required")
    frmDemo.add_item("Textarea", "textarea", "Some Value", "textarea", "")
    frmDemo.add_item("File", "file", "", "file", "")
    frmDemo.add_item("Picture", "picture", "", "picture", "")
    frmDemo.add_item("Checkbox", "checkbox", "", "checkbox", "")
    frmDemo.add_item("Hidden", "hidden", "Hidden value", "hidden", "")
    options = frmDemo.select_options([[1, "First"],
                                      [2, "Second"],
                                      [3, "Selected"],
                                      [4, "Other..."]], 3)
    frmDemo.add_item("Select", "select", options, "select", "")
    
    fldset= S_html.Fieldset("Fieldset", frmDemo.showHTML())
    page.add_bodyContent(fldset.showHTML())

    tableDemo = S_html.Table("Table Demo", "regularTable")
    tableDemo.add_header(["Column 1", "Column 2", "Column 3", "Column 4"])
    tableDemo.add_row(["Content 1", "Content 2", "Content 3", "Content 4"])
    tableDemo.add_row(["Content 5", "Content 6", "Content 7", "Content 8"])
    tableDemo.add_row(["Content 9", "Content 10", "Content 11", "Content 12"])
    tableDemo.add_footer("<td colspan='4'>Some footer information</td>")
    page.add_bodyContent(tableDemo.showHTML())

    fldset2= S_html.Fieldset("Fieldset", tableDemo.showHTML())
    page.add_bodyContent(fldset2.showHTML())

    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    result = page.showHTML()
  else:
    result = "Not Found"
    
  start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
  return result

================================
4.- Create the pi_html.css file:
================================
Use the example included or create your own

==========================
5.- POST and GET functions
==========================
Depending in what method are you passing your form data you can use the following functions to retrieve the fields content into a List:
	get = S_html.fetchQueryString(query_string.split("&"))
	post = S_html.fetchPost(environ['wsgi.input'])

You can access the fields content:
	get['get_field_name']
or
	post['post_field_name']
	
===============
6.- Have fun!!!
===============
Based on the demo use the trial and error process, and have fun!