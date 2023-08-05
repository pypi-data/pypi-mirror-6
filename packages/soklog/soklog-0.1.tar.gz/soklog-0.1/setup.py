# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages


install_requires = [
]

dependency_links = [
]

if __name__ == '__main__':
    setup(name='soklog',
          version='0.1',
          author=['Dominik "Socek" Długajczy'],
          author_email=['msocek@gmail.com', ],
          packages=find_packages(),
          install_requires=install_requires,
          dependency_links=dependency_links,
          test_suite='soklog.tests',
          )
