import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open('requirements.txt') as f:
    install_reqs = f.readlines()
    reqs = [str(ir) for ir in install_reqs]

with open(os.path.join(here, 'README.md')) as fp:
    long_description = fp.read()

setup(
    name='cert_mailer',
    version='1.0.0',
    description='cert mailer',
    author='Blockcerts - Gatech',
    long_description=long_description,
    packages=find_packages(),
    install_requires=reqs,
    include_package_data=True,
)