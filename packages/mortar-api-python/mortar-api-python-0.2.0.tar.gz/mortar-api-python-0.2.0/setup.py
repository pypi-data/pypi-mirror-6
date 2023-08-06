try:
    from setuptools import setup
except:
    from distutils.core import setup

from distutils.core import setup

try:
    long_description = []
    for line in open('README.md'):
        # Strip all images from the pypi description
        if not line.startswith('!') and not line.startswith('```'):
            long_description.append(line)
except IOError:
    # Temporary workaround for pip install
    long_description = ''

setup(name='mortar-api-python',
      version='0.2.0',
      description='Python API for Mortar',
      long_description=long_description,
      author='Mortar Data',
      author_email='info@mortardata.com',
      url='http://github.com/mortardata/mortar-api-python',
      namespace_packages = [
        'mortar'
      ],
      packages=[
          'mortar.api',
          'mortar.api.v2'
      ],
      license='LICENSE.txt',
      install_requires=[
          'requests'
      ]
)
