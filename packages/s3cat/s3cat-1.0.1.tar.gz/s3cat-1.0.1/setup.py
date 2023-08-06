from setuptools import setup
import sys
import os

try:
    ## Remove 'MANIFEST' file to force
    ## distutils to recreate it.
    ## Only in "sdist" stage. Otherwise
    ## it makes life difficult to packagers.
    if sys.argv[1] == "sdist":
        os.unlink("MANIFEST")
except:
    pass

setup(
    name="s3cat",
    version="1.0.1",
    scripts=['s3cat'],
    author="Ron Reiter",
    author_email="ron@crosswiselabs.com",
    url="http://github.com/crosswise/s3cat",
    license="MIT",
    description="s3cat lets you fetch all files under a certain directory (either raw or gzipped) into stdout.",
    long_description=open("README").read(),
    install_requires=open("requirements.txt").read().split("\n")
)
