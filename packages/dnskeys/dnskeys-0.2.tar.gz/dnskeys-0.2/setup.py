#!/usr/bin/env python

from distutils.core import setup

setup(name='dnskeys',
      version='0.2',
      description='A Python library for authenticating keys using DNS and DNSSEC',
      author='Iain R. Learmonth',
      author_email='irl@fsfe.org',
      url='http://www.github.com/irl/dnskeys/',
      packages=['dnskeys'],
      scripts=['getdnskeys'],
     )

