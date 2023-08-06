from setuptools import setup

setup(name='msbwt',
      version='0.1.2',
      description='Allows for merging and querying of multi-string BWTs',
      url='http://code.google.com/p/suspenders',
      author='James Holt',
      author_email='holtjma@cs.unc.edu',
      license='MIT',
      packages=['src/MUS'],
      install_requires=['pysam'],
      scripts=['bin/msbwt'],
      zip_safe=False)
