# -*- coding: utf-8 -*-

import os
from setuptools import (
    setup,
    find_packages,
)


here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
]

testing_requires = [
    'nose',
]

testing_extras = [
    'coverage',
]

docs_extras = [
    'Sphinx',
    'docutils',
    'pygments',
]

setup(
    name='hapis',
    version='0.1a2',
    description=(
        'A collection of packages that help with creating of plugins for '
        'Pyramid web framework'
    ),
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    author='Dmitry Arkhipov',
    author_email='grisumbras@gmail.com',
    url='https://github.com/grisumbras/hapis',
    license='MIT License',
    keywords='web pyramid configuration plugins',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=requires,
    tests_require=testing_requires,
    extras_require={
        'testing': testing_extras,
        'docs': docs_extras,
    },
    test_suite='nose.collector',
)
