# coding: utf-8

from setuptools import setup


setup(name='pigrate',
      version='0.0.3',
      description='Database schema migration tool written in Python',
      author='Eiichi Sato',
      author_email='sato.eiichi@gmail.com',
      url='https://github.com/eiiches/pigrate',
      download_url='https://github.com/eiiches/pigrate/archive/v0.0.3.tar.gz',
      keywords=['database', 'schema', 'migration'],
      requires=[],
      packages=['pigrate'],
      scripts=['bin/pigrate'])
