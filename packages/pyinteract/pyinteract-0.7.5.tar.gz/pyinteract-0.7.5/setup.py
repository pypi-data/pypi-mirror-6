import os
from setuptools import setup

# pyInteract, an interface to Responsys Interact Web Services
# Responsys offers Interact Web Services to offer automation of offered
# services available through the web UI.

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "pyinteract",
    version = "0.7.5",
    author = "Johan Nestaas, Mason Dixon",
    author_email = "johan.nestaas@oracle.com, mason.dixon@oracle.com",
    description = ("A Python API for the SOAP Web Services offered by "
        "responsys."),
    license = "BSD",
    keywords = "responsys interact marketing oracle marketing cloud",
    url = "https://bitbucket.org/johannestaas/responsys_pyinteract",
    packages=['interact'],
    long_description=read('README'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilities',
        'License :: OSI Approved :: BSD License',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        'Topic :: Office/Business',
    ],
    install_requires=[
        'suds',
    ],
)
