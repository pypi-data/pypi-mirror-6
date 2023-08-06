"""
Flask-Environ
-------------

Configure Flask from environment variables.
"""
from setuptools import setup


setup(
    name='Flask-EnvConfig',
    version='0.1.0',
    url='https://bitbucket.org/romabysen/flask-envconfig/',
    license='BSD',
    author='Lars Hansson',
    author_email='romabysen@gmail.com',
    description='Configure Flask from environment variables.',
    long_description=__doc__,
    py_modules=['flask_envconfig'],
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
    ]
)
