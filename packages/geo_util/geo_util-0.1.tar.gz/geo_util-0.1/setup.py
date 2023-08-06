try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

short_description = """
geo_util is a library containing various geomtry classes and functions.
""".strip()

setup(
    name='geo_util',
    version='0.1',
    author='Christian Fobel',
    author_email='christian@fobel.net',
    url='https://github.com/cfobel/python___geo_util',
    description=short_description,
    license='LGPL-3.0',
    packages=[
        'geo_util',
    ],
)
