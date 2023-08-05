from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='km2pg',
      version='0.2.0.1',
      description='Load kissmetrics website analytics data from an s3 bucket into a postgres database',
      url='http://github.com/shashank025/km2pg',
      author='Shashank Ramaprasad',
      author_email='shashank.ramaprasad+km2pg@gmail.com',
      license='MIT',
      packages=['km2pg'],
      scripts=['bin/km2pg',
               'bin/resolve_ids'],
      install_requires=[
        'sqlparse',
        'boto',
        'psycopg2',
        ],
      include_package_data=True,
      zip_safe=False)
