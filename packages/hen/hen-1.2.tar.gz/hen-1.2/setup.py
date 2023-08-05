import os
from setuptools import setup


here = os.path.dirname(os.path.abspath(__file__))


setup(
    name="hen",
    version="1.2",
    scripts=['hen'],
    #packages = find_packages(),
    author="Sergey Kirillov",
    author_email="sergey.kirillov@gmail.com",
    description="Process runner inspired by foreman",
    url="http://bitbucket.org/rushman/hen/",
    install_requires=['termcolor', 'pyyaml'],
    long_description=open(os.path.join(here, 'README.rst'), 'rb').read().decode('utf-8')
)
