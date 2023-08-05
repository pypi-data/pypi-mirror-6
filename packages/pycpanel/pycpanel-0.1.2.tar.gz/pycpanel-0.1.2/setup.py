from distutils.core import setup

setup(
    name='pycpanel',
    version='0.1.2',
    author='oznu',
    author_email='dev@oz.nu',
    packages=['pycpanel',],
    url='https://github.com/oznu/pycpanel',
    license='LICENSE.txt',
    description='Python module for the cPanel API.',
    long_description=open('README.rst').read(),
    install_requires=[
        "requests >= 2.0.0",
    ],
)
