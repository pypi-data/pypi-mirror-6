from distutils.core import setup

setup(
    name='cms-draggable-files',
    version='0.1.0',
    author='Jelena Kutalovskaja',
    author_email='jelena.kutalovskaja@gmail.com',
    packages=['cms_draggable_files'],
    scripts=[''],
    url='http://pypi.python.org/pypi/cms-draggable-files',
    license='LICENSE.txt',
    description='CMS placeholder can recieve dragged files and add to plugin by files extensions.',
    long_description=open('README.txt').read(),
    install_requires=[
        "django-cms >= 2.4.0",
        "django == 1.5.0",
    ],
)
