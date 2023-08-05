#!/usr/bin/env python
from distutils.core import setup

script_names = [
    'scripts/cleanjson',
    'scripts/rompy',
    'scripts/s3lod',
    'scripts/s3pub',
    'scripts/srep',
    ]

setup(name='abstrys-toolkit',
      author='Eron Hennessey',
      author_email='eron@abstrys.com',
      description='Useful command-line tools and scripts.',
      requires=['json', 'boto', 'PyYAML'],
      scripts=script_names,
      url='https://github.com/Abstrys/abstrys-toolkit',
      version='1.01',
      )
