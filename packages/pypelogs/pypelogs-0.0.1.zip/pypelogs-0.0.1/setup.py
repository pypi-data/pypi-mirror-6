from setuptools import setup, find_packages

setup(
    name='pypelogs',
    version='0.0.1',
    py_modules = ['pypelogs'],
    packages=find_packages(),
    license='GPL3',
    description='A generator-based tool and framework for piping log data (and other sources) from inputs to outputs, with any number of filters in between.',
    include_package_data = True,
    long_description=open('README.md').read(),
    author='Andy Jenkins',
    author_email='andy@gear11.com',
    url='https://github.com/gear11/pypelogs',
    install_requires=['pymongo>=2.6.3'],
    entry_points={
        'console_scripts': [
            'pl = pypelogs:main', 'pypelogs = pypelogs:main',
        ]

    }
)