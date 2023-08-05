from setuptools import setup, find_packages
import os

version = '0.2.0'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('js', 'chart', 'test_chart.txt')
    + '\n' +
    read('CHANGES.txt'))

setup(
    name='js.chart',
    version=version,
    description="fanstatic chart.js integration",
    long_description=long_description,
    classifiers=[],
    keywords='chartjs redturtle',
    author='RedTurtle Developers',
    url='https://github.com/RedTurtle/js.chart',
    author_email='sviluppoplone@redturtle.it',
    license='BSD',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'chart = js.chart:library',
            ],
        },
    )
