#encoding: utf-8
from distutils.core import setup

setup(
    name='python-delay',
    version='0.2',
    author='Flávio Ribeiro',
    author_email='email@flavioribeiro.com',
    packages=['delay'],
    url='http://pypi.python.org/pypi/python-delay/',
    license='LICENSE.txt',
    description='Python decorator to delay function calls',
    long_description=open('README.txt').read(),
)
