"""Setup script for the ur3e_case_study package."""
from setuptools import setup, find_packages

setup(
    name='ur3e_case_study',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'ipykernel', 
        'numpy<2.0', 
        'spatialmath-python', 
        'roboticstoolbox-python', 
        'spatialgeometry', 
        'pandas', 
        'matplotlib==3.9.0', 
        'docker>=7.1.0', 
        'pika', 
        'requests', 
        'pyhocon',
        'tqdm'
    ],
    include_package_data=True,
)