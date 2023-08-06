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
        'PyTest'
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


# from setuptools import setup, find_packages
#
# import configuration_panda
#
# with open('requirements.txt') as requirements_doc:
#     requirements = requirements_doc.read()
#
# setup(
#     name="configuration-panda",
#     packages=find_packages(),
#     version=configuration_panda.__version__,
#     author="Mike Dunn",
#     author_email="mike@eikonomega.com",
#     url="https://github.com/eikonomega/configuration_panda",
#     description="ConfigurationPanda provides easy loading and access to "
#                 "the data elements of JSON based configuration files.",
#     long_description=configuration_panda.__doc__,
#
#     install_requires=requirements,
#     #include_package_data=True,
#     package_data={
#         '': ['requirements.txt']
#     }
# )

