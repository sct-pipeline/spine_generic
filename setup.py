from setuptools import setup, find_packages
from codecs import open
from os import path

import spinegeneric

# Get the directory where this current file is saved
here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

req_path = path.join(here, 'requirements.txt')
with open(req_path, "r") as f:
    install_reqs = f.read().strip()
    install_reqs = install_reqs.split("\n")

setup(
    name='spinegeneric',
    version=spinegeneric.__version__,
    python_requires='>=3.6',
    description='Collection of scripts to process data for the Spine Generic project.',
    url='https://spine-generic.rtfd.io',
    author='NeuroPoly Lab, Polytechnique Montreal',
    author_email='neuropoly@googlegroups.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='',
    install_requires=install_reqs,
    entry_points={
        'console_scripts': [
            'sg_copy_to_derivatives = spinegeneric.scripts.copy_to_derivatives:main',
            'sg_deface_using_r = spinegeneric.scripts.deface_spineGeneric_usingR:main',
            'sg_generate_figure = spinegeneric.scripts.generate_figure:main',
            'sg_manual_correction = spinegeneric.scripts.manual_correction:main',
        ],
    },
)
