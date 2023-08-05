from __future__ import unicode_literals

from setuptools import setup, find_packages
import os.path

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='django-cache-magic',
      version='0.1.0',
      description='Django Cache Magic',
      author='Nathaniel Tucker',
      author_email='me@ntucker.me',
      url='https://github.com/ntucker/django-cache-magic',
      packages=find_packages(),
      include_package_data=True,
      install_requires=['django>=1.3', ],
      long_description=read('README.md'),
      license="BSD",
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
      ],
      )

