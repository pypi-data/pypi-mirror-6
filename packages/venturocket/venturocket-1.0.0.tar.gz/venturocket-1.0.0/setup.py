from setuptools import setup, find_packages

long_description = open('README.rst').read()

packages = find_packages(exclude=['tests", "tests.*'])

setup(
    name='venturocket',
    version='1.0.0',
    packages=packages,
    url='https://github.com/Venturocket/venturocket-api-python',
    license='LICENSE',
    author='Joe Linn',
    author_email='',
    description="The official python client library for Venturocket's API",
    long_description=long_description,
    install_requires=['requests'],
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP'
    ]
)