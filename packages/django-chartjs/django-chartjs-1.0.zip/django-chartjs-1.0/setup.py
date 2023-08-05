# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from os.path import abspath, dirname, join
from setuptools import find_packages, setup


def read_relative_file(filename):
    """Returns contents of the given file, whose path is supposed relative
    to this module."""
    with open(join(dirname(abspath(__file__)), filename)) as f:
        return f.read()


if __name__ == '__main__':  # ``import setup`` doesn't trigger setup().
    setup(
        name='django-chartjs',
        version=read_relative_file('VERSION').strip(),
        description="Django Chart.js and Hightchart ajax views",
        long_description=read_relative_file('README.rst'),
        classifiers=['Development Status :: 4 - Beta',
                     'Environment :: Web Environment',
                     'Framework :: Django',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: BSD License',
                     'Programming Language :: Python',
                     'Programming Language :: Python :: 2.7',
                     'Programming Language :: Python :: 3'],
        keywords='django chart chartjs highchart ajax class based views',
        author='Rémy Hubscher',
        author_email='hubscher.remy@gmail.com',
        url='https://github.com/novapost/django-chartjs',
        license='BSD Licence',
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=['six']  # depends on Django
    )
