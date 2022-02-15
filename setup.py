from setuptools import setup

setup(
    name='blenderize',
    version='0.1.1',
    description='loading CMCC mesh on blender',
    url='https://github.com/scausio/blenderize_29.git',
    author='Salvatore Causio',
    author_email='salvatore.causio@cmcc.it',
    install_requires=['xarray','scipy','shapely','fiona','netcdf4',
                      'numpy',
                      ],

)