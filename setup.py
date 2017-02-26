from setuptools import setup

setup(
    name='aloisius',
    version='0.3.1',
    description='Create/Update/Delete AWS CloudFormation stacks in parallel',
    author='Andreas Donig',
    author_email='andreas@innwiese.de',
    url='https://github.com/adonig/aloisius',
    license="FreeBSD License",
    packages=['aloisius'],
    install_requires=['boto3'],
    extras_require={
        'dev': [
            'autopep8',
            'flake8',
            'importmagic',
            'ipython',
            'jedi',
            'pytest',
            'troposphere',
        ]
    },
)
