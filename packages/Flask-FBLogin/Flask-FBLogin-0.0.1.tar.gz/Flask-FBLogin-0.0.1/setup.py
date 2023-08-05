"""
Flask-FBLogin
-----------------
Flask-FBLogin extends Flask-Login to use Facebook's OAuth2 authorization

Links
`````
* `documentation <http://flask-fblogin.readthedocs.org>`_
* `development version <https://github.com/marksteve/flask-fblogin>`_
"""
from setuptools import setup


setup(
    name='Flask-FBLogin',
    version='0.0.1',
    url='https://github.com/marksteve/flask-fblogin',
    license='MIT',
    author="Mark Steve Samson",
    author_email='hello@marksteve.com',
    description="Extends Flask-Login to use Facebook's OAuth2 authorization",
    long_description=__doc__,
    py_modules=['flask_fblogin'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'requests<1.0',
        'Flask-Login>=0.2,<0.3',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
