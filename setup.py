from setuptools import find_packages, setup
from typing import List


HYPHEN_E_DOT = '-e .'

def get_requirements(file_name:str)->List[str]:
    """
    Function to read and install packages from requirements.txt
    """
    with open(file_name) as file:
        requirements=file.readlines()
        requirements = [req.replace('\n','') for req in requirements]

        if HYPHEN_E_DOT in requirements:
            requirements.remove(HYPHEN_E_DOT)
    
    return requirements


setup(
    name='bill_splitter',
    version='0.0.1',
    author='Jason',
    author_email='jason_huynh32@hotmail.com',
    packages=find_packages(),
    install_requires=get_requirements('requirements.txt')
)