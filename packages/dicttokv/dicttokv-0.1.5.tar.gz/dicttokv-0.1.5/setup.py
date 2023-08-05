from distutils.core import setup

author = 'yuitest'
version = '0.1.5'
name = 'dicttokv'
url = 'https://github.com/yuitest/dicttokv'
short_description = (
    '`dicttokv` converts nested dictionary and list object'
    ' into key-value tuples.'
)
long_description = '''\
`dicttokv` converts nested dictionary and list object into key-value tuples.
tuples are useful for KeyValue Store and machine-learning.

Requirements
------------
* Python 2.7 or later (not support 3.x)

Features
--------
* tsv conversion method is included.

Setup
-----
::

   $ pip install dicttokv

History
-------
0.1.0 (2013-12)
0.1.5 (2014-01-01)

'''

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    author=author,
    packages=['dicttokv'],
    url=url,
    license='BSD',
)
