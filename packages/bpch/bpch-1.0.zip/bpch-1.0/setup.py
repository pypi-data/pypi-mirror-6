try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name = 'bpch',
      version = '1.0',
      author = 'Barron Henderson',
      author_email = 'barronh@ufl.edu',
      maintainer = 'Barron Henderson',
      maintainer_email = 'barronh@ufl.edu',
      py_modules = ['bpch'],
      requires = ['numpy (>=1.5)', 'matplotlib (>=1.0)'],
      url = 'http://github.com/barronh/bpch',
      download_url = 'http://github.com/barronh/bpch/tarball/master?egg=bpch-1.0'
      )
