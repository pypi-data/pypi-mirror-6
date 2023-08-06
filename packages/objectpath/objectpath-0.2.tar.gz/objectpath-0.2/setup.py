from setuptools import setup

setup(name='objectpath',
      version='0.2',
      description='The agile query language for JSON',
      url='http://adriank.github.io/ObjectPath',
      author='Adrian Kalbarczyk',
      author_email='adrian.kalbarczyk@gmail.com',
      license='GPLv3',
      packages=['objectpath','objectpath.utils','objectpath.core'],
      zip_safe=True)
