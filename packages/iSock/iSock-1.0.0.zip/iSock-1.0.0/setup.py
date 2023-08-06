from distutils.core import setup

setup(
    name='iSock',
    version='1.0.0',
    author='Damian Nowok',
    author_email='damian.nowok@gmail.com',
    packages=['isock', 'isock.test', 'isock.base'],
    scripts=['bin/example_isock.py'],
    url='http://pypi.python.org/pypi/isock/',
    license='LICENSE.txt',
    description='Simple client - server library based on TCP SocketServer',
    long_description=open('README.txt').read(),
)