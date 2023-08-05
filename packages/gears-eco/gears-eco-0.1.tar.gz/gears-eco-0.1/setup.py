import os
from setuptools import setup, find_packages

def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()

setup(
    name='gears-eco',
    version='0.1',
    license='ISC',
    author='Eugene Cheltsov',
    author_email='chill.icp@gmail.com',
    description='Eco: Embedded CoffeeScript templates for Gears',
    long_description=read('README.md'),
    packages=find_packages(),
    include_package_data=True,
    keywords = 'gears django-gears gears-eco',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ],
)