from distutils.core import setup
setup(name='Quandl',
      version='1.9.3',
      description = "Package for Quandl API access",
      author = "Mark Hartney, Chris Stevens",
      maintainer = 'Chris Stevens',
      maintainer_email = "connect@quandl.com",
      requirements = ['numpy','pandas'],
      license = 'MIT',
      packages=['Quandl'],
      )