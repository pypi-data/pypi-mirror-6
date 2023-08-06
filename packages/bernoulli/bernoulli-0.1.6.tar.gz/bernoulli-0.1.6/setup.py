from setuptools import setup

setup(name='bernoulli',
      version='0.1.6',
      description='A Python API for Bernoulli',
      url='https://github.com/bernoulli-metrics/bernoulli-python',
      author='Joe Gasiorek',
      author_email='joe.gasiorek@gmail.com',
      license='MIT',
      packages=['bernoulli'],
      install_requires=[
          'requests',
      ],
      test_suite='nose.collector',
      tests_require=['nose', 'httmock'],
      zip_safe=False
      )
