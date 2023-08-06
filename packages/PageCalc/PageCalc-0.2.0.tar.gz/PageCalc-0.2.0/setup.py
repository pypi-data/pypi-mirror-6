from distutils.core import setup

setup(
  name             = 'PageCalc',
  version          = '0.2.0',
  author           = 'saaj',
  author_email     = 'mail@saaj.me',
  packages         = ['pagecalc'],
  package_data     = {'pagecalc' : ['example/*']},  
  url              = 'http://code.google.com/p/pagecalc/',
  license          = 'LGPL',
  description      = 'Python pagination calculator',
  long_description = open('README.txt').read(),
  platforms        = ['Any'],
  classifiers      = [
    'Topic :: Utilities',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Intended Audience :: Developers'
  ]
)