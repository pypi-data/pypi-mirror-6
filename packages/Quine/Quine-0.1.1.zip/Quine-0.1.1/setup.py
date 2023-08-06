from distutils.core import setup

setup(
    name='Quine',
    version=open('CHANGES.txt').read().split()[0],
    author='Lucas Boppre Niehues',
    author_email='lucasboppre@gmail.com',
    packages=['quine'],
    url='http://pypi.python.org/pypi/Quine/',
    license='LICENSE.txt',
    description='Quine generator.',
    long_description=open('README.rst').read() + '\n\Last Updates\n-------------\n' + open('CHANGES.txt').read(),
)
