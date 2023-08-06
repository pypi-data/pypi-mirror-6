"""
==========
Flask-User
==========

Overview
--------

| Many Flask websites require the registration, authentication, and management of users.
| Each website often requires different customization of this process.

Flask-User aims to provide a robust package that offers:

* **Reliable** and **Feature Rich** user management functionality,
* **Ready to use** after an easy install and setup, and
* **Fully customizable** through well documented config settings and attributes, and
* **Secure** password hashing and token encryption and signing.

Status
------
!!News Flash: v0.3.2 fixes a bug where all confirmation emails were set to ling.thio@gmail.com!!

This package is relatively new. We are looking for alpha testers to give us feedback
on how it behaves in different usage scenarios. If something doesn't work the way
you expect it to work, please take the time to email ling [at] gmail.com and help us
reach outstanding quality quickly. Thanks!

We're also welcoming feature requests. In particular, we would like to know if there's
a need out there for database adapters other than the SQLAlchemyAdapter.

Functionality
-------------
::

    * Register with username         * Confirm email
    * Register with email            * Forgot password
    * Login                          * Change username
    * Logout                         * Change password

Documentation
-------------
* `View documentation here <https://pythonhosted.org/Flask-User/>`_

Revision History
----------------
* v0.3.2 Bugfix: All confirmation emails were sent to ling.thio@gmail.com
* v0.3.1 Added documentation for pythonhosted
* v0.3 Alpha release
       Confirm email, Forgot password, Reset password
* v0.2 Change username, Change password
* v0.1 Register, Login, Logout

Contact
-------
Ling Thio - ling.thio [at] gmail.com"""

from __future__ import print_function
from setuptools import setup

# class run_audit(Command):
#     """Audits source code using PyFlakes for following issues:
#         - Names which are used but not defined or used before they are defined.
#         - Names which are redefined without having been used.
#     """
#     description = "Audit source code with PyFlakes"
#     user_options = []
#
#     def initialize_options(self):
#         pass
#
#     def finalize_options(self):
#         pass
#
#     def run(self):
#         import os, sys
#         try:
#             import pyflakes.scripts.pyflakes as flakes
#         except ImportError:
#             print("Audit requires PyFlakes installed in your system.")
#             sys.exit(-1)
#
#         warns = 0
#         # Define top-level directories
#         dirs = ('flask', 'examples', 'scripts')
#         for dir in dirs:
#             for root, _, files in os.walk(dir):
#                 for file in files:
#                     if file != '__init__.py' and file.endswith('.py') :
#                         warns += flakes.checkPath(os.path.join(root, file))
#         if warns > 0:
#             print("Audit finished with total %d warnings." % warns)
#         else:
#             print("No problems found in sourcecode.")
#
setup(
    name='Flask-User',
    version='0.3.2',
    author='Ling Thio',
    author_email='ling.thio@gmail.com',
    url='http://github.com/lingthio/flask-user',
    license='Simplified BSD License',
    description='A user management extension for Flask (Register, Confirm, Login, Forgot password, etc.)',
    long_description=__doc__,
    packages=['flask_user'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'passlib',
        'py-bcrypt',
        'pycrypto',
        'Flask',                # Includes itsdangerous
        'Flask-Babel',
        'Flask-Login',
        'Flask-Mail',           # Includes blinker
        'Flask-SQLAlchemy',     # Includes SQLAlchemy
        'Flask-WTF',            # Includes WTForms
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: Dutch',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    #cmdclass={'audit': run_audit},
    #test_suite='flask.testsuite.suite'
)
