try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

config = {
  'description': 'My Project NAME',
  'author': 'Graham Monkman',
  'url': 'URL to get it at.',
  'download_url': 'Where to download it.',
  'author_email': 'gmonkman@mistymountains.biz',
  'version': '0.1',
  'install_requires': ['nose'],
  'packages': ['NAME'],
  'scripts': [],
  'name': 'Project NAME'
}

setup(**config)