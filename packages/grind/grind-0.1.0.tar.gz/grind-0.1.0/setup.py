import os

from setuptools import setup

curdir = os.path.dirname(__file__)
readme = os.path.join(curdir, 'README.rst')

setup(
    name='grind',
    version='0.1.0',
    description='delegate tasks to EC2 spot instances',
    long_description=open(readme).read(),
    author='Eugene Van den Bulke',
    author_email='eugene.vandenbulke@gmail.com',
    url='http://github.com/3kwa/grind',
    py_modules=['grind'],
    entry_points = {'console_scripts': ['grind = grind:main']},
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7'
        ],
     )
