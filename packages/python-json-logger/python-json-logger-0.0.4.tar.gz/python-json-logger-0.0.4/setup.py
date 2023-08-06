import sys, os

# if you are not using vagrant, just delete os.link directly,
# The hard link only saves a little disk space, so you should not care
if os.environ.get('USER','') == 'vagrant':
    del os.link

if sys.version_info < (2, 6):
    print(sys.stderr, "{}: need Python 2.6 or later.".format(sys.argv[0]))
    print(sys.stderror, "Your python is {}".format(sys.version))
    sys.exit(1)

from setuptools import setup

setup(
    name = "python-json-logger",
    version = "0.0.4",
    url = "http://github.com/madzak/python-json-logger",
    license = "BSD",
    description = "A python library adding a json log formatter",
    author = "Zakaria Zajac",
    author_email = "zak@madzak.com",
    package_dir = {'': 'src'},
    packages = [''],
    test_suite = "tests.tests",
    install_requires = ['setuptools'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Logging',
    ]
)
