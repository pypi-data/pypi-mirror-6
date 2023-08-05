"""
Flask-ini
---------

Allow Flask to be configured with ConfigParser ini files.
"""
from setuptools import setup

setup(
    name='Flask-ini',
    version='0.1.0',
    url='https://github.com/trendmicro/flask-ini',
    license='BSD',
    author='Rich Daley',
    author_email='rich@richd.me',
    description='Allow Flask to be configured with ConfigParser ini files',
    long_description=__doc__,
    py_modules=['flask_ini'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    test_suite='test_flask_ini'
)
