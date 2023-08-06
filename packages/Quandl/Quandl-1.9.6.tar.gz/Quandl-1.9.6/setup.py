from distutils.core import setup
requires = [
'numpy',
'pandas'
]


setup(name='Quandl',
      version='1.9.6',
      description = "Package for Quandl API access",
      author = "Mark Hartney, Chris Stevens",
      maintainer = 'Chris Stevens',
      maintainer_email = "connect@quandl.com",
      requires = requires,
      license = 'MIT',
      packages=['Quandl'],
      )