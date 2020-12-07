from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

setup(
    name='nwb-web-gui',
    version='0.1.2',
    description='Web graphical user interface for NWB conversion and exploring',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Luiz Tauffer and Vinicius Camozzato Vaz',
    author_email='luiz@taufferconsulting.com',
    url='https://github.com/catalystneuro/nwb-web-gui',
    keywords='nwb',
    packages=find_packages(),
    package_data={
        'assets': ['*'],
        'static': ['*']
    },
    include_package_data=True,
    install_requires=[
        'pynwb', 'numpy', 'nwbwidgets', 'dash', 'dash_daq', 'dash_bootstrap_components',
        'dash-cool-components', 'psutil', 'voila', 'pandas', 'jupyter', 'matplotlib', 'h5py',
        'jupyter-client'
    ]
)
