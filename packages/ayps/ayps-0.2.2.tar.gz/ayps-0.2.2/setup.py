#!/usr/bin/env python
from distutils.core import setup

sdict = {
        'name':'ayps',
        'version':'0.2.2',
        'description':'Asynchronous Python Shell: extended Twisted Conch Shell',
        'url':'https://github.com/deldotdr/ayps',
        'maintainer':'Dorian Raymer',
        'maintainer_email':'deldotdr@gmail.com',
        'install_requires':['Twisted'],
        'packages':['ayps'],
        'scripts':['scripts/ayps'],
        'keywords':['Twisted', 'shell', 'conch'],
        }

setup(**sdict)
