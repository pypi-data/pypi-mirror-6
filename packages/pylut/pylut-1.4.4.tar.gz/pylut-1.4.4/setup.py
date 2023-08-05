from distutils.core import setup

setup(
    name='pylut',
    version='1.4.4',
    author='Greg Cotten',
    author_email='gcgc90@gmail.com',
    packages=['pylut'],
    scripts=['bin/pylut'],
    url='http://pypi.python.org/pypi/PyLUT/',
    license='LICENSE.txt',
    description='Builds, modifies, visualizes, and converts 3D LUTs from popular .cube and .3dl formats.',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy",
        "docopt"
    ],
)