from setuptools import setup

setup(name='tstore',
      version='0.3',
      description='Table-oriented storage',
      url='https://github.com/langloisjp/tstore',
      author='Jean-Philippe Langlois',
      author_email='jpl@jplanglois.com',
      license='MIT',
      packages=['tstore'],
      install_requires=['psycopg2'],
      test_suite='tests.suite',
      zip_safe=True)
