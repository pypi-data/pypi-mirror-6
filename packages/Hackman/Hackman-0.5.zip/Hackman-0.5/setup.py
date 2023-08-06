from distutils.core import setup

setup(
    name='Hackman',
    version='0.5',
    author='Sebastien Tolron',
    author_email='sebastien@tolron',
    packages=['hackman', ],
    scripts=['bin/event.py'],
    url='http://pypi.python.org/pypi/Hackman/',
    license='LICENSE.txt',
    description='Hackman\'s Awesome package.',
    long_description=open('README.txt').read(),
)

