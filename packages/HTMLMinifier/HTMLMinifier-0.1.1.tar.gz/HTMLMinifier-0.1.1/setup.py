"""
HTMLMinifier
------------

A simple HTML5 minifier written in Python.
"""

from setuptools import setup

setup(
    name='HTMLMinifier',
    version='0.1.1',
    author='Chi-En Wu',
    author_email='',
    description='A simple HTML5 minifier written in Python.',
    long_description=__doc__,
    url='https://github.com/jason2506/HTMLMinifier',
    license='BSD 3-Clause License',
    packages=['HTMLMinifier'],
    zip_safe=False,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        "Topic :: Text Processing :: Markup :: HTML",
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
