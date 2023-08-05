from distutils.core import setup

setup(
    name='django-taobao',
    version='0.2.1',
    author='Jichao Ouyang',
    author_email='oyanglulu@gmail.com',
    packages=['taobao','taobao.templates'],
    url='https://github.com/jcouyang/django-taobao',
    license='LICENSE.txt',
    description='Taobao SDK for django.',
    long_description=open('README.rst').read(),
    install_requires=[
        "Django >= 1.6",
        "python-social-auth",
    ],
)

