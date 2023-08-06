#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='django-haystack-panel',
    version='0.2.0',
    description='A Django Debug Toolbar panel for Haystack',
    long_description=open('README.rst').read(),
    author='Chris Streeter',
    author_email='chris@chrisstreeter.com',
    url='http://github.com/streeter/django-haystack-panel',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'django-debug-toolbar>=1.0',
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
