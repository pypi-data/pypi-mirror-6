from distutils.core import setup

setup(
    name="s3cat",
    version="1.0",
    scripts=['s3cat'],
    author="Ron Reiter",
    author_email="ron@crosswiselabs.com",
    url="http://github.com/crosswise/s3cat",
    license="MIT",
    description="s3cat lets you fetch all files under a certain directory (either raw or gzipped) into stdout.",
    long_description=open("README").read()
)
