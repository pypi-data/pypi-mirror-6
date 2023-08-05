from distutils.core import setup

setup(
    name = 'S_html',
    version = '1.0.3',
    py_modules = ['S_html'],
    author = 'Sergio A. Hernandez',
    author_email = 'hernandez.sergio.a@gmail.com',
    url = 'http://ingelinux.wordpress.com/about/',
    description = 'A simple and easy to use HTML OOP Web Framework to use with WSGI',
    long_description = open('README.txt').read(),
    license = 'This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version',
    )