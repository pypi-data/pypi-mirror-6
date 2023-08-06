import os
from setuptools import setup, find_packages

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "farm-news",
    version = "0.9",
    install_requires=[
        'django-suit',
        'django-suit-redactor',
        'django-imagekit',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    author = "Jon Atkinson",
    author_email = "jon@wearefarm.com",
    description = "Provides news",
    license = "BSD",
    keywords = "news",
    url = "",
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
