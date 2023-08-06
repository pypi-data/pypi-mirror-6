import os
from setuptools import setup

version = __import__('simplemixins').get_version()

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
readme = f.read()
f.close()


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ''

setup(
    name = 'django-simple-mixins',
    version = version,
    packages = ['simplemixins'],
    include_package_data = True,
    license = 'BSD License',
    description = 'Mixins to use for Djangos Class Based Views.',
    long_description = readme,
    url = 'https://github.com/drager/django-simple-mixins',
    author = 'drager',
    author_email = 'drager@programmers.se',
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)