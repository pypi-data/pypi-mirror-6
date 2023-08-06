# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README_file = open(os.path.join(here, 'README.rst'))
README_lines = []
for nb, line in enumerate(README_file):
    if nb > 4:  # ignore the two first lines
        README_lines.append(line)

README = u'\n'.join(README_lines)

install_requires = [
    'setuptools',
    'zc.buildout',
    'PyYAML',
]

tests_require = [
    'nosexcover',
    'nose-progressive',
    'ipdbplugin',
    'unittest2',
]

setup(
    name='c2c.recipe.facts',
    version='1.2',
    description='Collect the puppet facter facts',
    long_description=README,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Framework :: Buildout :: Recipe',
        'Topic :: System :: Installation/Setup',
    ],
    author='Stéphane Brunner',
    author_email='stephane.brunner@camptocamp.com',
    url='http://github.com/sbrunner/c2c.recipe.facts',
    license='BSD',
    keywords='puppet facts facter',
    packages=find_packages(exclude=["*.tests", "*.tests.*"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=tests_require,
    entry_points={
        "zc.buildout": [
            "default = c2c_recipe_facts:Facts",
        ]
    }
)
