from distutils.core import setup

__version__ = '0.1-dev'

setup(name = 'traggr-api-client',
      packages = ['.'],
      version = __version__,
      description = 'API client for Test Results Aggregation system',
      author = 'Vitaliy Yakoviv',
      author_email = 'vyakoviv@gmail.com',
      url = 'https://github.com/witalick/traggr-api-client',
      # download_url = 'https://github.com/witalick/traggr-api-client/tarball/%s' % __version__,
      keywords = ['api', 'testing'],
      classifiers = [],
      install_requires=['requests'])
