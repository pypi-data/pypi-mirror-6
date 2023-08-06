import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
readme = open('README.md').read()
setup(
    name = "webdeployer",
    version = "0.0.4",
    author = "Royendgel Silberie",
    author_email = "royendgel@techprocur.com",
    description = ("Personal Deployer for site created with Flask and Django"),
    keywords = "deployer automation fabric",
    url = "https://github.com/royendgel",
    packages=['webdeployer', 'generators'],
    long_description=read('README.md'),
    classifiers=[
      'Operating System :: MacOS :: MacOS X',
      'Operating System :: Unix',
      'Development Status :: 3 - Alpha',
      'Topic :: Utilities',
      'Programming Language :: Python :: 2.7',
    ],
    include_package_data=True,
    install_requires=[
      'fabric',
      'jinja2',
      'pyCLI'
    ],
    package_data={
      # Include the generators templates
      'generators': ['*.tpl'],
    },
    scripts=['bin/webdeployer'],
)