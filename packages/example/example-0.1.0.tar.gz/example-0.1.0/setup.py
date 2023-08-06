from setuptools import setup

setup(
    name='example',
    version='0.1.0',
    author='Samuel "mansam" Lucidi',
    author_email="mansam@csh.rit.edu",
    packages=['example'],
    url='http://github.com/mansam/example',
    license='LICENSE',
    install_requires=[
    	'six'
    ],
    description='An example package.',
    long_description=open('README.rst').read()
)
