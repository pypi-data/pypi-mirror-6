from setuptools import setup, find_packages
from os.path import join, dirname
import multithreaddecorator

setup(
    name='multithreaddecorator',
    version=multithreaddecorator.__version__,
    author=multithreaddecorator.__author__,
    author_email=multithreaddecorator.__author_email__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
)
