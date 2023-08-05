from distutils.core import setup

setup(
    name = 'pyrSNVs',
    packages = ['pyrSNVs'], # this must be the same as the name above
    version = '0.1.0dev',
    description = 'A Python package for detection of regulatory SNVs',
    author = 'Guipeng Li',
    author_email = 'guipenglee@gmail.com',
    url = 'https://github.com/GuipengLi/pyrSNVs',   # use the URL to the github repo
    #download_url = 'https://github.com/GuipengLi/pyrSNVs/tarball/0.1dev', # I'll explain this in a second
    #download_url = 'https://github.com/GuipengLi/pyrSNVs/tarball/0.1.0dev', # I'll explain this in a second
    keywords = ['detection', 'regulatory', 'SNVs'], # arbitrary keywords
    #classifiers = [],
    license = 'GPL',
    long_description=open('README.md').read(),
)
