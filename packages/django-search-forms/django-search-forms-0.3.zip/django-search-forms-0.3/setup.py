# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from setuptools import setup, find_packages


with open('README.rst') as f:
    long_description = f.read()


setup(name='django-search-forms',
    version='0.3',
    description="Search forms for django",
    long_description=long_description,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='django search forms',
    author='Szymon Pyżalski',
    author_email='szymon@pythonista.net',
    license='BSD',
    packages=find_packages(),
    zip_safe=True,
    install_requires=[
        'django>=1.4.9',
    ],
    extras_require={
        'ajax': [
            'bob-ajax-selects>=1.3.3',
        ],
    },
)
