"""
Closure Templates (Soy)
~~~~~~~~~~~~~~~~~~~~~~~

This packages provides a set of functions used by Closure Templates
compiled to Python, and some utility classes for working with the
compiled source code.

For an introduction to Closure Templates in general, see the `project page`_.

To get started with using Closure Templates in Python, work though
`Hello World Using Python`_.

If you want to use Closure Templates from a `Flask`_ application, you
might want to use the `Flask-Soy`_ extension instead of using this
package directly.

.. _project page: https://developers.google.com/closure/templates/
.. _Hello World Using Python: https://bitbucket.org/lalinsky/closure-templates/wiki/Hello%20World%20Using%20Python
.. _Flask: http://flask.pocoo.org/
.. _Flask-Soy: https://pythonhosted.org/Flask-Soy/

"""

from setuptools import setup, find_packages

setup(
    name='soy',
    version='2012-12-21-p1',
    url='https://bitbucket.org/lalinsky/closure-templates',
    license='Apache',
    author='Lukas Lalinsky',
    author_email='lukas@oxygene.sk',
    description='Client- and server-side templating system for JavaScript, Java and Python.',
    long_description=__doc__,
    packages=find_packages('.'),
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        'License :: OSI Approved :: Apache Software License',
    ],
)

