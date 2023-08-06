import os
import sys
from setuptools import setup, find_packages

src_dir = os.path.dirname(__file__)


def get_version(src_dir):
    sys.path.insert(0, src_dir)
    import aws_helper
    return aws_helper.__version__


def read(filename):
    full_path = os.path.join(src_dir, filename)
    with open(full_path) as fd:
        return fd.read()

setup(name='aws_helper',
      version=get_version(src_dir),
      author='Michael Barrett',
      author_email='loki77@gmail.com',
      description='Helpers for dealing with AWS services.',
      long_description=read('README.rst'),
      packages=find_packages(),)
