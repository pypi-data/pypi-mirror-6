# -*- coding: utf-8 -*-
from distutils.core import setup

setup(name='s3mongobkp',
      version='0.1',
      description='MongoDB backups to cloud Amazon S3',
      author='Rodion S.',
      author_email='python@profserver.ru',
      url='https://bitbucket.org/rodion_s/s3mongobkp',
      license='GPL',
      platforms=('Linux', 'MacOS X'),
      keywords = ('amazon', 'mongodb', 's3', 'backup'),
      packages=['s3mongobkp'],
      package_dir={'s3mongobkp': 'src/s3mongobkp'},
      scripts = ['bin/s3mongobkp_run.py'],
      data_files=[('/etc', ['cfg/s3mongobkp.conf'])],
      requires=['boto (>=2.7.0)'],
      )
