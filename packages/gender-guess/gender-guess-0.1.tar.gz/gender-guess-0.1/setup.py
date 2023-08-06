#!/usr/bin/python

from distutils.core import setup
from distutils.extension import Extension


_gender = Extension('gender_guess._gender', ['gender.i', 'gender.c'],
                    swig_opts=['-modern', '-Wall'])#, '-outdir','notwanted-pwrapper'])

setup(name='gender-guess',
      version='0.1',
      description='''

      ''',
      author='Alexander Weigl',
      author_email='spamling@web.de',
      url='http://github.com/areku/get-gender_guess',
      packages = ['gender_guess'],
      ext_modules = [_gender],
      package_data={'gender_guess':['*.txt']},
     )
