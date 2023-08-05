from distutils.core import setup

setup(
    name='validator.py',
    version='0.2.1',
    author='Samuel "mansam" Lucidi',
    author_email="mansam@csh.rit.edu",
    packages=['validator'],
    url='http://pypi.python.org/pypi/validator.py/',
    license='LICENSE',
    description='A library for validating that dictionary values meet certain sets of parameters. Much like form validators, but for dicts.',
    long_description=open('README.md').read()
)


