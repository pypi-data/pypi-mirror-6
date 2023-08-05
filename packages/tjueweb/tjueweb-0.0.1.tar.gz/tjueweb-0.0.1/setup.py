from setuptools import setup

import os

license = ""

if os.path.isfile("LICENSE"):
    with open('LICENSE') as f:
        license = f.read()

setup(
    name='tjueweb',
    version='0.0.1',
    packages=['tjueweb'],
    package_data={'': ['tjueweb/*']},
    url='https://github.com/tesseract2048/tju-eweb',
    license=license,
    author='tess3ract',
    author_email='hty0807@gmail.com',
    description='A client library for e.tju.edu.cn (tju-eweb)',
    install_requires=['urllib2', 'urllib'],
)
