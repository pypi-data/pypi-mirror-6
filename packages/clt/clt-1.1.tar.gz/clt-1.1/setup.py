from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

# versions < 2.7 support
install_requires = []
try:
    import argparse  # noqa
except ImportError:
    install_requires.append('argparse')

setup(name='clt',
      version='1.1',
      description='CLI template processor',
      long_description=long_description,
      author='ffeast',
      author_email='ffeast@gmail.com',
      url='https://github.com/ffeast/clt',
      install_requires=install_requires,
      scripts=['clt'])
