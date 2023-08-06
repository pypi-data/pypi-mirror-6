# from distutils.core import setup
from setuptools import setup

__version__ = '0.2'

setup(name = 'traggr-api-client',
      packages = ['.'],
      version = __version__,
      description = 'API client for Test Results Aggregation system',
      author = 'Vitaliy Yakoviv',
      author_email = 'witalick@gmail.com',
      url = 'https://github.com/witalick/traggr-api-client',
      keywords = ['api', 'testing'],
      classifiers = [],
      install_requires=['requests'])
