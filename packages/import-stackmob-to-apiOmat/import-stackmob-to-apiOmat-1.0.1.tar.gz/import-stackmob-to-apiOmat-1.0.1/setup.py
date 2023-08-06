'''
Created on 29.04.2013

@author: phimi
'''
from setuptools import setup, find_packages
setup(
    name = "import-stackmob-to-apiOmat",
    description = "Import your data from Stackmob to apiOmat",
    url = "https://github.com/apinaut/apiOmat-import-stackmob",
    version = "1.0.1",
    scripts=['ImportStackmobData/import-stackmob-to-apiOmat'],
    packages = find_packages(),
)