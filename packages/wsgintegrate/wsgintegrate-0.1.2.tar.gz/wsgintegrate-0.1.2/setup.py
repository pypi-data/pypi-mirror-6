from setuptools import setup
import os

version = '0.1.2'

# description
try:
  filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'README.txt')
  description = file(filename).read()
except:
  description = ''

dependencies = ['webob']

setup(name='wsgintegrate',
      version=version,
      description='WSGI integration layer',
      long_description=description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Jeff Hammel',
      author_email='k0scist@gmail.com',
      url='http://k0s.org/',
      license='GPL',
      packages=['wsgintegrate'],
      include_package_data=True,
      zip_safe=False,
      install_requires=dependencies,
      entry_points="""
      [console_scripts]
      wsgintegrate = wsgintegrate.main:main
      """,
      )
