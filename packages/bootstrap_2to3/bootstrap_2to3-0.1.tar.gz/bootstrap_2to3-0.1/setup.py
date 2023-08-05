from distutils.core import setup

setup(
    name='bootstrap_2to3',
    version='0.1',
    author='Jayesh',
    author_email='jayesh@jayeshv.info',
    scripts=['bootstrap_2to3.py'],
    url='https://github.com/jayeshv/bootstrap_2to3',
    license='BSD licence',
    description='Script to migrate bootstrap 2 templates to bootstrap3.',
    long_description=open('README.md').read(),
)
