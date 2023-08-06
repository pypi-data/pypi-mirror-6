try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="pessimum",
    author="Hugo Bastien",
    author_email="hugobast@gmail.com",
    url="https://github.com/hugobast/pessimum.git",
    version="0.0.1",
    packages=[
        "pessimum"
    ],
    tests_require=["mock"],
    install_requires=[
        "nose",
        "setuptools"
    ],
    test_suite='tests',
    license="MIT License",
    description="Tells you the top 10 longest running tests in your run",
    long_description=open("README.txt").read(),
    entry_points = {
        'nose.plugins.0.10': [
            'pessimum = pessimum:Pessimum'
        ]
    }
)