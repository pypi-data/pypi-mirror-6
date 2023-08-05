from setuptools import setup


VERSION = '0.3.0'


setup(
    name='wordpress-reader',
    version=VERSION,
    url='https://bitbucket.org/onetouchteam/wordpress-reader',
    license='BSD',
    description='A Python library to pull data out of Wordpress.',
    author='onetouchteam.com',
    author_email='dev@onetouchteam.com',
    packages=['wordpress_reader'],
    install_requires=['MySQL-python'],
)
