from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    long_description = f.read()

with open('requirements.txt', 'r') as f:
    install_requires = [w for w in f.read().strip().split('\n') if not w.startswith('-e')]

setup(
    name='nwb-web-gui',
    version='0.1.6',
    description='Web graphical user interface for NWB conversion and exploring',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Luiz Tauffer and Vinicius Camozzato Vaz',
    author_email='luiz@taufferconsulting.com',
    url='https://github.com/catalystneuro/nwb-web-gui',
    keywords='nwb',
    packages=find_packages(),
    package_data={
        'nwb_web_gui': [
            'static/*',
            'templates/*',
            'dashapps/pages/converter/example_schemas/*'
        ]
    },
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        'console_scripts': ['nwbgui=nwb_web_gui.cmd_line:cmd_line_shortcut']
    }
)
