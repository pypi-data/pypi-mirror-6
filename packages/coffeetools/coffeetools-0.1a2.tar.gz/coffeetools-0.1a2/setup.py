try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


VERSION = open('VERSION').read().strip()

REQUIRES = open('requirements.txt').read().strip().split('\n')


setup(
  name='coffeetools',
  version=VERSION,
  description=(
    'Tools for using CoffeeScript with Python.'
    ),
  author='Stefan Zimmermann',
  author_email='zimmermann.code@gmail.com',
  url='http://bitbucket.org/userzimmermann/python-coffeetools',

  license='LGPLv3',

  install_requires=REQUIRES,
  packages=[
    'coffeetools',
    'coffeetools.jinja',
    ],

  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved ::'
    ' GNU Library or Lesser General Public License (LGPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development',
    'Topic :: Utilities',
    ],
  keywords=[
    'coffee', 'tools', 'script', 'coffeescript', 'javascript',
    'jinja', 'jinja2', 'jinjatools', 'template', 'tag', 'extension',
    'python3',
    ],
  )
