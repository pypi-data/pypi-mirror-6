from setuptools import setup

setup(name='umdh',
      version='0.2',
      description='Tools for working with University of Michigan dining hall data',
      url='http://github.com/davidwilemski/umdh',
      author='David Wilemski',
      author_email='david@davidwilemski.com',
      license='ISC',
      packages=['umdh'],
      scripts=['umdh/umdh.py'],
      install_requires=[
          'requests',
      ],
      tests_require=['nose'],
      zip_safe=False)
