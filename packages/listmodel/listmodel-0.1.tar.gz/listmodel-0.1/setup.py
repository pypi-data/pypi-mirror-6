from setuptools import setup

_name = 'listmodel'

setup(name=_name,
      version='0.1',
      description='Listmodel is a Python library for building iterators for various list sources (XML documents, Text documents, JSON objects etc.) in a unified manner.',
      url='http://github.com/jackuess/%s' % _name,
      author='Jacques de Laval',
      author_email='chucky@wrutschkow.org',
      license='LGPL v3',
      packages=[_name],
      install_requires= [
          'jsonpath-rw',
          'lxml',
          'requests'
      ],
      zip_safe=False)
