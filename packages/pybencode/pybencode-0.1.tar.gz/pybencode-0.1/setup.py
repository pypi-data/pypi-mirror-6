from distutils.core import setup
from bencode import __version__

setup(
    name='pybencode',
    version=__version__,
    packages=['bencode'],
    url='https://github.com/FnuGk/pybencode',
    license='MIT',
    author='FnuGK',
    author_email='jesperbroge@gmail.com',
    description='Simple bencode implementation in python'
)
