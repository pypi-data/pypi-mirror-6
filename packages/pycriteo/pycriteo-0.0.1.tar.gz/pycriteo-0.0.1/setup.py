from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='pycriteo',
    version='0.0.1',
    description='Simple library to access the Criteo API',
    long_description=readme(),
    url='http://github.com/storborg/funniest',
    author='Francesco Della Vedova',
    author_email='fdellavedova@gmail.com',
    license='Apache 2.0',
    packages=['pycriteo'],
    install_requires=[
        'suds==0.4',
        'unicodecsv==0.9.4',
    ]
)
