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
    version="1.0.2",
    scripts=['s3cat'],
    author="Ron Reiter",
    author_email="ron@crosswiselabs.com",
    url="http://github.com/crosswise/s3cat",
    license="MIT",
    description="s3cat lets you fetch all files under a certain directory (either raw or gzipped) into stdout.",
    long_description=open(os.path.join(os.path.dirname(__file__), "README")).read(),
    install_requires=open(os.path.join(os.path.dirname(__file__), "requirements.txt")).read().split("\n")
)
