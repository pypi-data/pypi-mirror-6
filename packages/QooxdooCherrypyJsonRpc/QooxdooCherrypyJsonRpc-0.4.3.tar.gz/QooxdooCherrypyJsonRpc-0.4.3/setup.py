from distutils.core import setup

setup(
  name             = 'QooxdooCherrypyJsonRpc',
  version          = '0.4.3',
  author           = 'saaj',
  author_email     = 'mail@saaj.me',
  packages         = ['qxcpjsonrpc', 'qxcpjsonrpc.test'],
  url              = 'http://code.google.com/p/qooxdoo-cherrypy-json-rpc/',
  license          = 'LGPL',
  description      = 'Qooxdoo-specific CherryPy-based JSON RPC-server',
  long_description = open('README.txt').read(),
  install_requires = ['CherryPy >= 3.2'],
  platforms        = ['Any'],
  classifiers      = [
    'Topic :: Communications',
    'Framework :: CherryPy',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.3',
    'Intended Audience :: Developers'
  ]
)