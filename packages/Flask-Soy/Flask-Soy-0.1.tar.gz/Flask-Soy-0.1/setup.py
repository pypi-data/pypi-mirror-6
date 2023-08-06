"""
Flask-Soy
~~~~~~~~~

Provides support for `Closure Templates`_ (Soy) in Flask.

.. _Closure Templates: https://developers.google.com/closure/templates/

"""

from setuptools import setup

setup(
    name='Flask-Soy',
    version='0.1',
    url='https://bitbucket.org/lalinsky/flask-soy',
    license='Apache',
    author='Lukas Lalinsky',
    author_email='lukas@oxygene.sk',
    description='Provides support for Closure Templates (Soy) in Flask.',
    long_description=__doc__,
    py_modules=['flask_soy'],
    zip_safe=False,
    platforms='any',
    install_requires=['Flask', 'Soy'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

