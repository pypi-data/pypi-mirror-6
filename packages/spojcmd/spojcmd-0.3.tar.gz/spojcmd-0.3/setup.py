import os
from setuptools import setup, find_packages


name = 'spojcmd'
version = '0.3'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name = name,
    version = version,
    author = "Rachit Nimavat",
    author_email = "iamrachiit@gmail.com",
    description = ("command line tool for spoj.com "),
    license = "BSD",
    keywords = "spoj problems command line algorithmic problems",
    url = "http://github.com/tvanicraath/spojcmd",
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "Topic :: Education",
        "Intended Audience :: Customer Service",
    ],
    install_requires=[
        'setuptools',
        'prettytable',
        'argparse>=1.2.1',
        'requests>=1.1.0',
        'BeautifulSoup>=3.2.1',
        ],
    entry_points={
        'console_scripts': [
            'spojcmd = spojcmd.main:runner',
            ]
        },
)
