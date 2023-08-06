from distutils.core import setup
from setuptools import setup, find_packages
setup(
    name='cms-draggable-files',
    version='0.1.4',
    author='Jelena Kutalovskaja',
    author_email='jelena.kutalovskaja@gmail.com',
    url='http://pypi.python.org/pypi/cms-draggable-files',
    license='LICENSE.txt',
    packages = ['cms_draggable_files',],
    description='CMS placeholder can recieve dragged files and add to plugin by files extensions.',
    long_description=open('README.txt').read(),
)
