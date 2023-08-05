#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='Proximate',
    author='George V. Reilly',
    author_email='george@reilly.org',
    version='0.1.1',
    packages=find_packages(),
    description='Simple HTTP Reverse Proxy that aggregates multiple hosts '
    'into a unified namespace',
    long_description=open('README.md').read(),
    url='https://github.com/cozi/proximate',
    package_data={},
    zip_safe=False,
    install_requires=[
        'Paste',
        'WSGIProxy',
    ],
    entry_points={
        'console_scripts': [
            'proximate=proximate.proxy:proximate',
            ]
    },
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: Proxy Servers',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
    ],
    platforms='any',
)
