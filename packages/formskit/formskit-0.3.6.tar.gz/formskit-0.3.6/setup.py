# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'python-dateutil',
    'six',
]

if __name__ == '__main__':
    setup(name='formskit',
          version='0.3.6',
          author=['Dominik "Socek" Długajczy'],
          author_email=['msocek@gmail.com', ],
          packages=find_packages(),
          test_suite='formskit.tests.get_all_test_suite',
          )
