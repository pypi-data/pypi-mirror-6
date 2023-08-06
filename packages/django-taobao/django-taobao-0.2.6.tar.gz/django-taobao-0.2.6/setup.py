from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    long_description = f.read()
    
setup(
    name='django-taobao',
    version='0.2.6',
    author='Jichao Ouyang',
    author_email='oyanglulu@gmail.com',
    packages = find_packages(exclude=['examples', 'tests']),
    include_package_data = True,
    url='https://github.com/jcouyang/django-taobao',
    license='MIT',
    keywords='django, taobao, oauth, api',
    description='Taobao SDK for django.',
    # long_description=open('README.rst').read()
)

