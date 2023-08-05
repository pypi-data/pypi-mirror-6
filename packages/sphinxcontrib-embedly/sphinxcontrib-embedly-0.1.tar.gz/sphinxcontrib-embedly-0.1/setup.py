# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
This package contains the Embedly Sphinx extension.

This extension enable you to embed anything using Embedly_ .
Following code is sample::

   .. embedly:: http://www.youtube.com/watch?v=M_eYSuPKP3Y

.. _Embedly: http://embed.ly/
'''

requires = ['Sphinx>=0.6', 'Embedly']

setup(
    name='sphinxcontrib-embedly',
    version='0.1',
    url='http://bitbucket.org/birkenfeld/sphinx-contrib',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-embedly',
    license='BSD',
    author='Jannis Leidel',
    author_email='jannis@leidel.info',
    description='Sphinx "embedly" extension',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
)
