# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages


install_requires = [
    'venusian',
    'soklog',
    'mock',
    'six',
]

dependency_links = [
    'https://github.com/socek/soklog/tarball/master#egg=soklog-0.1',
]

if __name__ == '__main__':
    setup(name='soktest',
          version='0.1.1',
          author=['Dominik "Socek" Długajczy'],
          author_email=['msocek@gmail.com', ],
          packages=find_packages(),
          install_requires=install_requires,
          dependency_links=dependency_links,
          test_suite='soktest.tests.get_all_test_suite',
          )
