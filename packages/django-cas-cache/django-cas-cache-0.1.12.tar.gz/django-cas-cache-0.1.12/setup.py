from distutils.core import setup

setup(
    name='django-cas-cache',
    version='0.1.12',
    packages=[
        'cascache',
        'cascache.backends',
    ],
    license='MIT',
    long_description=open('pypi.rst').read(),
    author="Anentropic",
    author_email="ego@anentropic.com",
    url="https://github.com/anentropic/django-cas-cache",
)
