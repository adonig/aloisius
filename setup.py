from setuptools import setup

setup(
    name='aloisius',
    version='0.4.1',
    description='Create/Update/Delete AWS CloudFormation stacks in parallel',
    author='Andreas Donig',
    author_email='andreas@innwiese.de',
    url='https://github.com/adonig/aloisius',
    license="FreeBSD License",
    packages=['aloisius'],
    install_requires=['boto3', 'six'],
)
