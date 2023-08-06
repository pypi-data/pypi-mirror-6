from setuptools import setup

setup(
      name = 'keywrapper',
      version = '0.1.0',
      description = 'Extremely simple key-value storage wrapper',
      url = 'https://github.com/lbosque/keywrapper',
      author = 'Luis Bosque',
      author_email = 'luisico@gmai.com',
      license = 'BSD-3',
      packages = ['keywrapper'],
      install_requires = ['redis'],
      zip_safe = True
)
