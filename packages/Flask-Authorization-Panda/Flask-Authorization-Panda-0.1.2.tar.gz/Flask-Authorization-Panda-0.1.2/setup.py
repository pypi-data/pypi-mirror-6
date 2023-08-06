"""
Flask-Authorization-Panda
-------------

Flask Authorization for Pandas!

Provides decorators for Flask view methods that implement various
authentication schemes.

"""
from setuptools import setup, find_packages
import flask_authorization_panda


setup(
    name='Flask-Authorization-Panda',
    version=flask_authorization_panda.__version__,
    url='https://github.com/eikonomega/flask-authorization-panda',
    license='MIT',
    author='Mike Dunn',
    author_email='mike@eikonomega.com',
    description='Flask Authorization for Pandas!',
    long_description=flask_authorization_panda.__doc__,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'PyTest',
        'pytest-cov'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

