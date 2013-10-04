# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages
setup(
    name='django-reversion-compare-auditlog',
    version='0.0.1',
    author=u'Azamat Tokhtaev',
    author_email='krik123@gmail.com',
    url='https://github.com/ITAttractor/django-reversion-compare-auditlog',
    license='BSD License',
    description='Uses django-reversion-compare to show a standalone table where user can see all the changes to the objects',
    long_description=open('README.md').read(),
    zip_safe=False,
    packages=find_packages(),
    setup_requires=['django-reversion', 'django-reversion-compare'],
    install_requires=['django-reversion', 'django-reversion-compare']
)
